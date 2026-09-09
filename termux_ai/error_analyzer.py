def build_context(command, stdout, stderr, code):
    return f'الأمر: {command}\nرمز الخروج: {code}\nSTDOUT:\n{stdout[-4000:]}\nSTDERR:\n{stderr[-6000:]}'
