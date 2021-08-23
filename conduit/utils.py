# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""


def jwt_identity(payload):
    from conduit.user.models import User  # noqa
    return User.get_by_id(payload)


def identity_loader(user):
    return user.id
