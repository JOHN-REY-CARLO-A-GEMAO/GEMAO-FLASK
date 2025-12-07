from flask import flash

def Alert_Success(message):
    flash(message, 'success')

def Alert_Fail(message):
    flash(message, 'fail')
