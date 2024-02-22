import inspect

from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from fields import model_fields, model_meta_fields


def process_docstring(app, what, name, obj, options, lines):  # noqa
    # This causes import errors if left outside the function
    from django import forms
    from django.db import models

    # Only look at objects that inherit from Django's base model class
    if inspect.isclass(obj) and issubclass(obj, models.Model):
        # Grab the field list from the meta class
        fields = obj._meta.fields
        lines.append("")

        for field in fields:
            # Do not document AutoFields
            if type(field).__name__ == "AutoField" and field.primary_key:
                continue

            type(field).__name__
            # Decode and strip any html out of the field's help text
            help_text = strip_tags(force_unicode(field.help_text))

            # Decode and capitalize the verbose name, for use if there isn't
            # any help text
            force_unicode(field.verbose_name).capitalize()

            lines.append(".. attribute::  %s" % field.name)
            lines.append("    ")
            # Add the field's type to the docstring
            if isinstance(field, models.ForeignKey):
                to = field.rel.to
                line = "    {}(':class:`~{}.{}`')".format(
                    type(field).__name__, to.__module__, to.__name__
                )
            elif isinstance(field, models.OneToOneField):
                to = field.rel.to
                line = "    {}(':class:`~{}.{}`')".format(
                    type(field).__name__, to.__module__, to.__name__
                )
            else:
                line = "    %s" % type(field).__name__
            if not field.blank:
                line = line + " (Required)"
            if hasattr(field, "auto_now") and field.auto_now:
                line = line + " (Automatically set when updated)"
            if hasattr(field, "auto_now_add") and field.auto_now_add:
                line = line + " (Automatically set when created)"
            lines.append(line)
            if help_text:
                lines.append("")
                # Add the model field to the end of the docstring as a param
                # using the help text as the description
                lines.append("    %s" % help_text)
            lines.append("    ")
            f = model_fields[type(field).__name__]
            for key in sorted(f.iterkeys()):

                if (
                    hasattr(field, key)
                    and getattr(field, key) != f[key]
                    and getattr(field, key)
                ):
                    attr = getattr(field, key)
                    if key == "error_messages":
                        error_dict = {}
                        for i in sorted(attr.iterkeys()):
                            error_dict[i] = force_unicode(attr[i])
                        attr = error_dict
                    if key == "validators":
                        v = []
                        for i in sorted(attr):
                            n = ":class:`~{}.{}`".format(
                                type(i).__module__, type(i).__name__
                            )
                            v.append(n)
                        attr = v
                    lines.append(f"    :param {key}: {attr}")
        lines.append("")
        lines.append(".. attribute:: Meta")
        lines.append("")
        for key in sorted(model_meta_fields.iterkeys()):
            if (
                hasattr(obj._meta, key)
                and getattr(obj._meta, key) != model_meta_fields[key]
            ):
                lines.append(f"    {key} = {getattr(obj._meta, key)}")
                lines.append("")

    # Only look at objects that inherit from Django's base model class
    if inspect.isclass(obj):
        if issubclass(obj, forms.Form) or issubclass(obj, forms.ModelForm):
            # Grab the field list from the meta class
            fields = obj.base_fields
            lines.append("")

            for field in fields:
                f = obj.base_fields[field]
                # Decode and strip any html out of the field's help text
                if hasattr(f, "help_text"):
                    help_text = strip_tags(force_unicode(f.help_text))
                # Decode and capitalize the verbose name, for use if there isn't
                # any help text
                force_unicode(f.label).capitalize()

                lines.append(".. attribute::  %s" % field)
                lines.append("")
                # Add the field's type to the docstring
                field_inst = obj.base_fields[field]
                line = "   :class:`~{}.{}`".format(
                    type(field_inst).__module__, type(field_inst).__name__
                )
                if field_inst.required:
                    line = line + " (Required)"
                lines.append(line)
                lines.append("")
                if hasattr(f, "error_messages") and f.error_messages:
                    msgs = {}
                    for key, value in f.error_messages.items():
                        msgs[key] = force_unicode(value)
                    lines.append(":kwarg error_messages:  %s" % msgs)
                if f.help_text:
                    # Add the model field to the end of the docstring as a param
                    # using the help text as the description
                    lines.append(":kwarg help_text: %s" % help_text)
                if hasattr(f, "initial") and f.initial:
                    lines.append(":kwarg initial: %s" % f.initial)
                if hasattr(f, "localize"):
                    lines.append(":kwarg localize: %s" % f.localize)
                if hasattr(f, "validators") and f.validators:
                    line = []
                    for v in f.validators:
                        line.append(
                            ":class:`~{}.{}`".format(
                                type(v).__module__, type(v).__name__
                            )
                        )
                    lines.append(":kwarg validators: %s" % line)
                lines.append(":kwarg widget: %s" % type(f.widget).__name__)
                lines.append("")

    # Return the extended docstring
    return lines


def setup(app):
    # Register the docstring processor with sphinx
    app.connect("autodoc-process-docstring", process_docstring)
    app.add_crossref_type(
        directivename="admin",
        rolename="admin",
        indextemplate="pair: %s; admin",
    )
    app.add_crossref_type(
        directivename="command",
        rolename="command",
        indextemplate="pair: %s; command",
    )
    app.add_crossref_type(
        directivename="context_processors",
        rolename="context_processors",
        indextemplate="pair: %s; context_processors",
    )
    app.add_crossref_type(
        directivename="form",
        rolename="form",
        indextemplate="pair: %s; form",
    )
    app.add_crossref_type(
        directivename="formfield",
        rolename="formfield",
        indextemplate="pair: %s; formfield",
    )
    app.add_crossref_type(
        directivename="manager",
        rolename="manager",
        indextemplate="pair: %s; manager",
    )
    app.add_crossref_type(
        directivename="middleware",
        rolename="middleware",
        indextemplate="pair: %s; middleware",
    )
    app.add_crossref_type(
        directivename="model",
        rolename="model",
        indextemplate="pair: %s; model",
    )
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="settings",
        rolename="settings",
        indextemplate="pair: %s; settings",
    )
    app.add_crossref_type(
        directivename="signal",
        rolename="signal",
        indextemplate="pair: %s; signal",
    )
    app.add_crossref_type(
        directivename="token",
        rolename="token",
        indextemplate="pair: %s; token",
    )
    app.add_crossref_type(
        directivename="validator",
        rolename="validator",
        indextemplate="pair: %s; validator",
    )
    app.add_crossref_type(
        directivename="view",
        rolename="view",
        indextemplate="pair: %s; view",
    )
