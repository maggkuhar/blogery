from flask import Blueprint, render_template, request, redirect, url_for
from .logic import get_all_templates, get_template, add_template, update_template, delete_template, increment_template_usage
from constants import TEMPLATE_FORMATS

bp = Blueprint('templates_bp', __name__, template_folder='templates')


@bp.route("/templates")
def templates():
    fmt = request.args.get("format", "")
    subgroup = request.args.get("subgroup", "")
    items = get_all_templates(format=fmt or None, subgroup=subgroup or None)
    return render_template("templates.html",
        templates=items,
        template_formats=TEMPLATE_FORMATS,
        filters={"format": fmt, "subgroup": subgroup},
        tab="templates",
    )


@bp.route("/templates/add", methods=["GET", "POST"])
def templates_add():
    if request.method == "POST":
        add_template(request.form)
        return redirect(url_for("templates_bp.templates"))
    fmt = request.args.get("format", "")
    subgroup = request.args.get("subgroup", "")
    return render_template("template_form.html",
        item=None, template_formats=TEMPLATE_FORMATS,
        action="Добавить шаблон", preset_format=fmt, preset_subgroup=subgroup)


@bp.route("/templates/edit/<int:template_id>", methods=["GET", "POST"])
def templates_edit(template_id):
    tmpl = get_template(template_id)
    if not tmpl:
        return redirect(url_for("templates_bp.templates"))
    if request.method == "POST":
        update_template(template_id, request.form)
        return redirect(url_for("templates_bp.templates"))
    return render_template("template_form.html",
        item=tmpl, template_formats=TEMPLATE_FORMATS,
        action="Сохранить", preset_format="", preset_subgroup="")


@bp.route("/templates/delete/<int:template_id>", methods=["POST"])
def templates_delete(template_id):
    delete_template(template_id)
    return redirect(url_for("templates_bp.templates"))


@bp.route("/templates/use/<int:template_id>", methods=["POST"])
def templates_use(template_id):
    increment_template_usage(template_id)
    return redirect(url_for("templates_bp.templates"))
