from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField


class DealReportForm(FlaskForm):
    period = SelectField('惩罚期限', choices=[('0', "不做处理"), \
                                          ('1', "3小时"), ('2', "1天"), ('3', "3天"), ('4', '一个月')], default='1')
    submit = SubmitField('处理')
