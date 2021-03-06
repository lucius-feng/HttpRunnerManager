from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import TestCaseInfo, ModuleInfo, ProjectInfo


def run_by_single(index, base_url, config):
    """
    加载单个case用例信息
    :param index: int or str：用例索引
    :param base_url: str：环境地址
    :param config: str or int：配置索引
    :return: dict
    """
    testcase_dict = {
        'name': 'testset description',
        'config': {
            'name': 'base_url config',
            'request': {
                'base_url': base_url,
            }
        },
        'api': {},
        'testcases': []
    }
    if config != '':  # 指定了配置
        try:
            config_request = eval(TestCaseInfo.objects.get(id=config).request)
        except ObjectDoesNotExist:
            return testcase_dict
        config_request.get('config').get('request').setdefault('base_url', base_url)
        testcase_dict['config'] = config_request.pop('config')

    try:
        obj = TestCaseInfo.objects.get(id=index)
    except ObjectDoesNotExist:
        return testcase_dict

    include = eval(obj.include)
    request = eval(obj.request).pop('test')

    if include:
        for test_info in include:
            try:
                id = test_info[0]
                pre_request = eval(TestCaseInfo.objects.get(id=id).request)
            except ObjectDoesNotExist:
                return testcase_dict
            testcase_dict['testcases'].append(pre_request.pop('test'))
        testcase_dict['testcases'].append(request)
    else:
        testcase_dict['testcases'].append(request)
    return testcase_dict


def run_by_batch(test_list, base_url, config, type=None, mode=False):
    """
    批量组装用例数据
    :param test_list:
    :param base_url: str: 环境地址
    :param type: str：用例级别
    :param mode: boolean：True 异步 False: 同步
    :return: list
    """
    testcase_lists = []

    if mode:
        for index in range(len(test_list) - 3):
            form_test = test_list[index].split('=')
            value = form_test[1]
            if type == 'project':
                testcase_lists.extend(run_by_project(value, base_url, config))
            elif type == 'module':
                testcase_lists.extend(run_by_module(value, base_url, config))

    else:
        if type == 'project':
            for value in test_list.values():
                testcase_lists.extend(run_by_project(value, base_url, config))
        elif type == 'module':
            for value in test_list.values():
                testcase_lists.extend(run_by_module(value, base_url, config))
        else:

            for index in range(len(test_list) - 2):
                form_test = test_list[index].split('=')
                index = form_test[1]
                testcase_lists.append(run_by_single(index, base_url, config))
    return testcase_lists


def run_by_module(id, base_url, config):
    """
    组装模块用例
    :param id: int or str：模块索引
    :param base_url: str：环境地址
    :return: list
    """
    testcase_lists = []
    obj = ModuleInfo.objects.get(id=id)
    test_index_list = TestCaseInfo.objects.filter(belong_module=obj, type=1).values_list('id')
    for index in test_index_list:
        testcase_lists.append(run_by_single(index[0], base_url, config))
    return testcase_lists


def run_by_project(id, base_url, config):
    """
    组装项目用例
    :param id: int or str：项目索引
    :param base_url: 环境地址
    :return: list
    """
    testcase_lists = []
    obj = ProjectInfo.objects.get(id=id)
    module_index_list = ModuleInfo.objects.filter(belong_project=obj).values_list('id')
    for index in module_index_list:
        module_id = index[0]
        testcase_lists.extend(run_by_module(module_id, base_url, config))
    return testcase_lists
