import json
import os
from datetime import datetime, timedelta
from os.path import join, dirname

import django
import requests
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()


from devman.models import Student, Manager, Team, Project


def get_student_info(student_id):
    result = {'id': student_id}
    student = (
        Student.objects
        .filter(id=student_id, is_active=True)
        .prefetch_related('teams')
        .first()
    )
    if not student:
        return
    result['name'] = student.name
    result['level'] = student.level
    result['status'] = student.status
    result['start_time'] = student.available_time_start
    result['finish_time'] = student.available_time_finish
    result['project_date'] = student.project_date
    current_team = (
        student
        .teams
        .filter(is_active=True)
        .select_related('manager')
        .prefetch_related('students')
        .first()
    )
    if current_team:
        result['team_id'] = current_team.id
        result['current_team'] = current_team.title
        result['call_time'] = current_team.call_time
        result['students'] = [
            f'{x.name} {x.id}' for x in current_team.students.all()
        ]
        result['PM'] = f"{current_team.manager.name} {current_team.manager.id}"
    return result


def set_student(data):
    student = Student.objects.get(id=data['id'])
    student.update(
        project_date=data['week'],
        available_time_start=datetime.strptime(data['start_time'], '%H:%M'),
        available_time_finish=datetime.strptime(data['end_time'], '%H:%M'),
        status=data['status']
    )


def get_manager_info(manager_id):
    result = {'id': manager_id}
    manager = (
        Manager.objects
        .prefetch_related('ts')
        .filter(id=manager_id)
        .first()
    )
    if not manager:
        return None
    result['teams'] = []
    for team in manager.ts.filter(is_active=True):
        result['teams'].append({
            'call_time': team.call_time,
            'team_id': team.id,
            'team_title': team.title,
            'trello': str(team.trello),
            'tg_chat': team.tg_chat,
            'description': str(team.description),
            'students': [f'{x.__str__()} {x.id}' for x in team.students.all()]
        })
    result['name'] = manager.name
    result['working_time'] = (manager.starttime, manager.finishtime)
    return result


def set_new_time(manager_id, starttime, finishtime):
    manager = Manager.objects.get(id=manager_id)
    manager.starttime, manager.finishtime = starttime, finishtime
    manager.save()


def get_team_info(id):
    team = (
        Team.objects
        .prefetch_related('students')
        .select_related('manager')
        .get(id=id)
    )
    result = {'team_id': id}
    result['project_name'] = team.title
    result['students'] = [f'{x.__str__()} {x.id}' for x in team.students.all()]
    result['PM'] = team.manager.__str__()
    result['call_time'] = team.call_time
    result['description'] = str(team.description)
    result['trello'] = team.trello
    return result


def close_team(team_id, manager_id, final_status=''):
    team = Team.objects.select_related('manager').get(id=team_id)
    if manager_id != team.manager.id:
        return None
    team.is_active = False
    team.final_status = final_status
    team.save()
    return team.id


def finalize_teams(start_date):
    teams = Team.objects.filter(is_active=True, date=start_date).prefetch_related('students')
    teams.update(is_active=False)
    teams.students.update(status=1)


def create_trello(project_id):

    project = Project.objects.get(id=project_id)
    project_end_date = project.startdate + timedelta(days=7)
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    API_KEY = os.environ.get("API_KEY")
    TOKEN = os.environ.get("TOKEN")

    project_full_name = f'Проект {project.name}, [{project.startdate}-{project_end_date}]'

    url = "https://api.trello.com/1/organizations"

    headers = {
        "Accept": "application/json"
    }

    query = {
        'displayName': project_full_name,
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )

    org = json.loads(response.text)
    #print(org)

    teams = Team.objects.all()

    for team in teams:

        students = ''
        for student in team.students.all():
            students += f'{student.name} '

        board_name=f'{team.call_time} - {students}'

        url = "https://api.trello.com/1/boards/"

        query = {
            'name': board_name,
            'key': API_KEY,
            'token': TOKEN,
            'idOrganization':org['id'],
            'prefs_background':team.manager.trello_bg_color,
            'desc':f'PM команды: {team.manager.name}',
            'prefs_permissionLevel':'private',

        }

        response = requests.request(
            "POST",
            url,
            params=query
        )

        board = json.loads(response.text)
        #print(board['url'])

        url = f"https://api.trello.com/1/boards/{board['id']}"
        team.trello = url
        team.save()

        query = {
            'key': API_KEY,
            'token': TOKEN,
            'closed':'false'
        }

        response = requests.request(
            "PUT",
            url,
            params=query
        )

        url = f"https://api.trello.com/1/boards/{board['id']}/lists"

        headers = {
            "Accept": "application/json"
        }

        query = {
            'name': 'Архив',
            'pos': 'bottom',
            'key': API_KEY,
            'token': TOKEN
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )


if __name__ == '__main__':

    print(get_manager_info('@belgorod_admin')['teams'][0]['trello'])
