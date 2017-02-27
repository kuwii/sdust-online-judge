from django.shortcuts import render, redirect, reverse, get_object_or_404
from rest_api.permissions import GROUP_NAME_ROOT, GROUP_NAME_USER_ADMIN, GROUP_NAME_CLIENT
from rest_api.permissions import GROUP_NAME_PROBLEM_ADMIN, GROUP_NAME_CATEGORY_ADMIN
from rest_api.permissions import GROUP_NAME_JUDGE_ADMIN, GROUP_NAME_CLIENT_ADMIN

from rest_api.models import *
from django.contrib.auth.models import Group


# == Utils =============================================================================================================

def user_info(request):
    user = request.user
    if user.is_authenticated():
        group = set()
        for it in user.groups.all().values('name'):
            group.add(it['name'])
        info = {
            'is_authenticated': True,
            'user': user,
            'group': group
        }
    else:
        info = {
            'is_authenticated': False,
        }
    return info


def has_problem_access(info):
    group = info['group']
    return GROUP_NAME_ROOT in group or GROUP_NAME_PROBLEM_ADMIN in group or GROUP_NAME_CATEGORY_ADMIN in group


def has_submission_access(info):
    group = info['group']

    return has_problem_access(info) or GROUP_NAME_JUDGE_ADMIN in group or GROUP_NAME_CLIENT_ADMIN in group


def is_problem_admin(info):
    group = info['group']
    return GROUP_NAME_ROOT in group or GROUP_NAME_PROBLEM_ADMIN in group


def is_category_admin(info):
    return has_problem_access(info)


def is_client_admin(info):
    group = info['group']
    return GROUP_NAME_ROOT in group or GROUP_NAME_CLIENT_ADMIN in group


def is_user_admin(info):
    group = info['group']
    return GROUP_NAME_USER_ADMIN in group or GROUP_NAME_ROOT in group


def is_judge_admin(info):
    group = info['group']
    return GROUP_NAME_JUDGE_ADMIN in group or GROUP_NAME_ROOT in group


# == Views =============================================================================================================

def to_home(request):
    return redirect(reverse('homepage'))


def homepage(request):
    info = user_info(request)

    return render(request, 'homepage.html', {
        'user': info
    })


def personal_info(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    return render(request, 'personalInfo.html', {
        'user': info
    })


def personal_edit(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    return render(request, 'personalEdit.html', {
        'user': info
    })


def personal_password(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    return render(request, 'personalPassword.html', {
        'user': info
    })


def problem_home(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not has_problem_access(info):
        return redirect(reverse('homepage'))

    return render(request, 'problemHome.html', {
        'user': info
    })


def problem_meta(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'problemMeta.html', {
        'user': info
    })


def problem_meta_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'problemMetaCreate.html', {
        'user': info
    })


def problem_meta_instance(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaInfo.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_description(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaDescription.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_description_create(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaDescriptionCreate.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_description_instance(request, mid, did):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    description = get_object_or_404(Description.objects, id=int(did))

    return render(request, 'problemMetaDescriptionInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'description': description
    })


def problem_meta_sample(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaSample.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_sample_create(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaSampleCreate.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_sample_instance(request, mid, sid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    sample = get_object_or_404(Sample.objects, id=int(sid))

    return render(request, 'problemMetaSampleInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'sample': sample
    })


def problem_meta_test(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaTest.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_test_create(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaTestCreate.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_test_instance(request, mid, tid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    test_data = get_object_or_404(TestData.objects, id=int(tid))

    return render(request, 'problemMetaTestInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'test': test_data,
        'test_in': test_data.get_test_in(),
        'test_out': test_data.get_test_out()
    })


def problem_meta_problem(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaProblem.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_problem_create(request, mid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))

    return render(request, 'problemMetaProblemCreate.html', {
        'user': info,
        'meta_problem': meta_problem
    })


def problem_meta_problem_instance(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemInfo.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_limits(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemLimits.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_limits_create(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemLimitsCreate.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_limits_instance(request, mid, pid, lid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))
    limit = get_object_or_404(Limit.objects, id=int(lid))

    return render(request, 'problemMetaProblemLimitsInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob,
        'limit': limit
    })


def problem_meta_problem_spj(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemSpecial.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_spj_create(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemSpecialCreate.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_spj_instance(request, mid, pid, sid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))
    spj = get_object_or_404(SpecialJudge.objects, id=int(sid))

    code = spj.get_code()

    return render(request, 'problemMetaProblemSpecialInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob,
        'spj': spj,
        'code': code
    })


def problem_meta_problem_iw(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemIW.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_iw_create(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemIWCreate.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_iw_instance(request, mid, pid, iw_id):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))
    iw = get_object_or_404(InvalidWord.objects, id=int(iw_id))

    return render(request, 'problemMetaProblemIWInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob,
        'iw': iw
    })


def problem_meta_problem_test(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemTest.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_test_create(request, mid, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemMetaProblemTestCreate.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob
    })


def problem_meta_problem_test_instance(request, mid, pid, tid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_problem_admin(info):
        return redirect(reverse('homepage'))

    meta_problem = get_object_or_404(MetaProblem.objects, id=int(mid))
    prob = get_object_or_404(Problem.objects, id=int(pid))
    test = get_object_or_404(ProblemTestData.objects, id=int(tid))

    return render(request, 'problemMetaProblemTestInstance.html', {
        'user': info,
        'meta_problem': meta_problem,
        'problem': prob,
        'test': test
    })


def problem(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'problem.html', {
        'user': info
    })


def problem_instance(request, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    prob = get_object_or_404(Problem.objects, id=int(pid))

    return render(request, 'problemInstance.html', {
        'user': info,
        'pid': pid,
        'problem': prob
    })


def problem_category(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not has_submission_access(info):
        return redirect(reverse('homepage'))

    return render(request, 'problemCategory.html', {
        'user': info
    })


def problem_category_instance(request, cid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    category = get_object_or_404(Category.objects, id=int(cid))

    return render(request, 'problemCategoryInstance.html', {
        'user': info,
        'cat': category
    })


def problem_category_dir(request, cid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    category = get_object_or_404(Category.objects, id=int(cid))

    return render(request, 'problemCategoryDir.html', {
        'user': info,
        'cat': category
    })


def problem_submissions(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'submission.html', {
        'user': info
    })


def problem_submission_info(request, sid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_category_admin(info):
        return redirect(reverse('homepage'))

    submission = get_object_or_404(Submission.objects, id=int(sid))

    return render(request, 'submissionInfo.html', {
        'user': info,
        'submission': submission
    })


def client_clients(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'client.html', {
        'user': info,
    })


def client_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'clientCreate.html', {
        'user': info,
    })


def client_instance(request, cid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    client = get_object_or_404(Client.objects, id=int(cid))

    return render(request, 'clientInfo.html', {
        'user': info,
        'client': client
    })


def client_categories(request, cid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    client = get_object_or_404(Client.objects, id=int(cid))

    return render(request, 'clientCategories.html', {
        'user': info,
        'client': client
    })


def client_categories_create(request, cid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    client = get_object_or_404(Client.objects, id=int(cid))

    return render(request, 'clientCategoriesCreate.html', {
        'user': info,
        'client': client
    })


def client_category_instance(request, cid, rid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    client = get_object_or_404(Client.objects, id=int(cid))
    relation = get_object_or_404(ClientCategory.objects, id=int(rid))

    return render(request, 'clientCategoryInstance.html', {
        'user': info,
        'client': client,
        'relation': relation
    })


def client_users(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'clientUser.html', {
        'user': info,
    })


def client_user_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'clientUserCreate.html', {
        'user': info,
    })


def client_user_instance(request, username):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_client_admin(info):
        return redirect(reverse('homepage'))

    client_user = get_object_or_404(User.objects.filter(groups__name=GROUP_NAME_CLIENT), username=username)

    return render(request, 'clientUserInstance.html', {
        'user': info,
        'clientUser': client_user
    })


def users(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_user_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'users.html', {
        'user': info
    })


def user_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_user_admin(info):
        return redirect(reverse('homepage'))

    groups = Group.objects.exclude(name=GROUP_NAME_CLIENT)

    return render(request, 'userCreate.html', {
        'user': info,
        'groups': groups
    })


def user_instance(request, username):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_user_admin(info):
        return redirect(reverse('homepage'))

    groups = Group.objects.exclude(name=GROUP_NAME_CLIENT)
    u_info = get_object_or_404(User.objects.exclude(groups__name=GROUP_NAME_CLIENT), username=username)

    return render(request, 'userInstance.html', {
        'user': info,
        'groups': groups,
        'u_info': u_info
    })


def submit_problem(request, pid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not has_problem_access(info):
        return redirect(reverse('homepage'))

    prob = get_object_or_404(Problem.objects.filter(available=True, deleted=False), id=int(pid))
    environments = Environment.objects.filter(available=True, deleted=False).order_by('id')

    return render(request, 'SubmissionCreate.html', {
        'user': info,
        'problem': prob,
        'envs': environments
    })


def environments(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'environments.html', {
        'user': info
    })


def environment_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'environmentCreate.html', {
        'user': info
    })


def environment_instance(request, eid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    env = get_object_or_404(Environment.objects.all(), id=int(eid))

    return render(request, 'environmentInstance.html', {
        'user': info,
        'env': env
    })


def judges(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'judges.html', {
        'user': info
    })


def judge_create(request):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    return render(request, 'judgeCreate.html', {
        'user': info
    })


def judge_instance(request, jid):
    info = user_info(request)

    if not info['is_authenticated']:
        return redirect(reverse('login_page'))

    if not is_judge_admin(info):
        return redirect(reverse('homepage'))

    judge = get_object_or_404(Judge.objects.all(), id=int(jid))
    env = Environment.objects.filter(deleted=False).order_by('id')
    judge_environments = judge.environment.all()

    return render(request, 'judgeInstance.html', {
        'user': info,
        'jid': jid,
        'judge': judge,
        'environments': env,
        'judge_environments': judge_environments
    })


def login(request):
    if request.user.is_authenticated():
        return redirect(reverse('homepage'))
    return render(request, 'login.html')
