# -*- coding: utf-8 -*-
__author__ = 'vahid'


def clean_list(l):
    return [j for j in [i.strip().strip('"') for i in l] if j]


def list_hash(l):
    return hash(tuple(l))
