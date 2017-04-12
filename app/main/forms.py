# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .. import photos


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1, 30)])
    body = TextAreaField('body', validators=[DataRequired(), Length(1, 140)])
    photo = FileField('插入图片', render_kw={'multiple': True}, validators=[FileAllowed(photos, u'只能上传图片！')])
    post = SubmitField('发表')


class ProfileForm(FlaskForm):
    about_me = StringField('about_me', validators=[Length(1, 30)])
    sex = SelectField('性别', choices=[('male', 'male'), ('female', 'female')], coerce=str)
    location = StringField('城市', validators=[Length(1, 30)])
    edit = SubmitField('修改')


class EditPasswordForm(FlaskForm):
    old_password = StringField('旧密码', validators=[Length(1, 30)])
    new_password = PasswordField('新密码', validators=[Length(1, 30)])
    confirm_password = PasswordField('确认密码', validators=[EqualTo('new_password')])
    submit = SubmitField('修改')


class EditPersonalForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1, 30)])
    body = TextAreaField('body', validators=[DataRequired(), Length(1, 140)])
    post = SubmitField('发表')
    save = SubmitField('保存')


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('评论')


class UserSearchForm(FlaskForm):
    body = StringField('用户名', validators=[DataRequired()])
    submit = SubmitField('搜索')


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'只能上传图片！'),
                                  FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')


class ReplyForm(FlaskForm):
    body = StringField('内容', validators=[DataRequired()])
    submit = SubmitField('回复')


class AlbumForm(FlaskForm):
    name = StringField('新相册名', validators=[DataRequired()])
    submit = SubmitField('创建')


class PhotoForm(FlaskForm):
    photo = FileField('上传新的照片', validators=[FileAllowed(photos, u'只能上传图片！'),
                                  FileRequired(u'文件未选择！')])
    name = StringField('照片描述', validators=[DataRequired()])
    sumbit = SubmitField(u'上传')
