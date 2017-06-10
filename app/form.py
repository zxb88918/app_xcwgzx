# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp, IPAddress

class testform(Form):
    fqd = SelectField(u'   分前端：', choices=[
                                            ('0', u'前进路总前端'),
                                            ('1', u'建安大道分前端'),
                                            ('2', u'劳动路分前端'),
                                            ('3', u'光明路分前端'),
                                            ('4', u'水语花城分前端')
                                            ])
    cnumac = StringField(u'   高频cnu-mac：', validators=[DataRequired(), Regexp('[0-9a-fA-F]{12}')])
    submit = SubmitField(u'提交')


class cnuform(Form):
    cnumac = StringField(u'   高频cnu-mac：', validators=[DataRequired(), Regexp('[0-9a-fA-F]{12}')])
    submit = SubmitField(u'提交')

class rssiform(Form):
    wocip = StringField(u'   woc ip：', validators=[DataRequired(), IPAddress()])
    submit = SubmitField(u'提交')