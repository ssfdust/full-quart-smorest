# pylint: disable=line-too-long
"""
模板相关的Invoke模块
"""
import logging
import re
import os
import datetime
import shutil

from invoke import task
from tasks.app.consts import (
    BACKUP_PERMISSIONS_FILE,
    NEW_PERMISSIONS_FILE,
    PERMISSIONS_FILE,
    ADDED_ROLE,
    ADDED_SU,
    ADDED_MAPPING,
    ADDED_PERMISSIONS,
    EOF_ROLES,
    EOF_MAPPING,
    EOF_SU,
    EOF_PEMISSIONS,
)
from tasks.app._utils import create_dirs

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

@task
def generate_config(context):
    # pylint: disable=unused-argument
    """
    新建配置内容，根据提示新建配置

    用法:
    $ invoke app.boilerplates.generate_config
    """
    from tasks.app.config import Config
    from tasks.app.renders import render_config_to_toml

    create_dirs()

    # Genrate configuration
    configs = Config()
    configs.set_configurations()

    render_config_to_toml(configs)

    log.info("配置文件生成完毕.")


@task(
    help={
        "module_name": "模块名称",
        "module_title": "模块标题（注释用）",
        "module_name_singular": "模块单例名",
        "description": "模块描述",
    }
)
def crud_module(
    context, module_name="", module_name_singular="", module_title="", description=""
):
    # pylint: disable=unused-argument
    """
    新建一个增删改查模块
    来源：frol/flask-restplus-server-example

    用法:
    $ inv app.boilerplates.crud-module --module-name=articles \
                --module-name-singular=article \
                --description=文章的增删改查API \
                --module_title=文章

    """
    try:
        import jinja2
    except ImportError:
        log.critical("缺少jinja2模块，请通过`pip install jinja2`安装")
        return

    if not module_name:
        log.critical("请提供模块名")
        return

    if not re.match("^[a-zA-Z0-9_]+$", module_name):
        log.critical("模块名中包含特殊字符" "([a-zA-Z0-9_]+)")
        return

    if not module_name_singular:
        module_name_singular = module_name[:-1]

    module_path = "app/modules/%s" % module_name

    if not module_title:
        module_title = " ".join([word.capitalize() for word in module_name.split("_")])

    model_name = "".join(
        [word.capitalize() for word in module_name_singular.split("_")]
    )

    if os.path.exists(module_path):
        log.critical("模块 `%s` 已存在.", module_name)
        return

    os.makedirs(module_path)

    env = jinja2.Environment(
        autoescape=True,
        loader=jinja2.FileSystemLoader("tasks/app/templates/crud_module"),
    )

    # 从.AUTHOR中获取author
    for template_file in (
        "__init__",
        "models",
        "params",
        "resources",
        "schemas",
    ):
        template = env.get_template("%s.py.template" % template_file)
        template.stream(
            module_name=module_name,
            module_name_singular=module_name_singular,
            module_title=module_title,
            module_namespace=module_name.replace("_", "-"),
            model_name=model_name,
            description=description,
            year=datetime.date.today().year,
        ).dump("%s/%s.py" % (module_path, template_file))

    permissions_adder(context, model_name=model_name, module_title=module_title)

    log.info("模块 `%s` 创建成功.", module_name)

    log.info("请在app/factory.py中的ENABLED_MODULES中添加新模块以激活。")


@task(help={"revert": "还原"})
def apply_changes(_, revert=False):
    """
    应用新模块的权限
    """

    if os.path.exists(BACKUP_PERMISSIONS_FILE) and not revert:
        os.remove(BACKUP_PERMISSIONS_FILE)
    if os.path.exists(NEW_PERMISSIONS_FILE) and revert:
        os.remove(NEW_PERMISSIONS_FILE)
    if not revert:
        orders = [
            [PERMISSIONS_FILE, BACKUP_PERMISSIONS_FILE],
            [NEW_PERMISSIONS_FILE, PERMISSIONS_FILE],
        ]
    else:
        orders = [
            [PERMISSIONS_FILE, NEW_PERMISSIONS_FILE],
            [BACKUP_PERMISSIONS_FILE, PERMISSIONS_FILE],
        ]
    for orig, dst in orders:
        if os.path.exists(orig):
            log.info("移动%s到%s", orig, dst)
            shutil.move(orig, dst)
        else:
            log.critical("%s不存在应用失败", orig)
            return
    log.info("应用完毕")


@task(help={"model_name": "模块ORM名", "module_title": "模块名"})
def permissions_adder(context, model_name="", module_title=""):
    # pylint: disable=unused-argument
    """
    为权限文件新增新的模块权限

    用法:
    $ inv app.boilerplates.permissions-adder --module-name=articles \
                --module_title=文章

    """

    added_role = ADDED_ROLE.format(model_name=model_name)
    added_permissions = ADDED_PERMISSIONS.format(model_name=model_name)
    added_su = ADDED_SU.format(model_name=model_name, module_title=module_title)
    added_mapping = ADDED_MAPPING.format(model_name=model_name)

    with open("app/modules/auth/permissions.py") as f:
        text = f.read()

    for orig, subs in [
        [EOF_ROLES, added_role],
        [EOF_PEMISSIONS, added_permissions],
        [EOF_SU, added_su],
        [EOF_MAPPING, added_mapping],
    ]:
        text = text.replace(orig, subs)

    with open("app/modules/auth/permissions.new.py", "w") as f:
        f.write(text)

    log.info("新权限文件 `%s` 生成成功.\n", "app/modules/auth/permissions.new.py")
    log.info("请编辑后替换旧权限文件，并执行`invoke app.db.update-app-permissions`")


@task
def generate_docker_compose(context):
    # pylint: disable=unused-argument
    from tasks.app.config import Config
    from tasks.app.renders import render_config_to_dockercompose

    configs = Config().load_configurations()
    render_config_to_dockercompose(configs)
