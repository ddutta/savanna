#def before_feature(context, feature):
#    model.init(environment='test')
#    if 'browser' in feature.tags:
#        context.server = simple_server.WSGIServer(('', 8000))
#        context.server.set_app(web_app.main(environment='test'))
#        context.thread = threading.Thread(target=context.server.serve_forever)
#        context.thread.start()
#        context.browser = webdriver.Chrome()
#
#def after_feature(context, feature):
#    if 'browser' in feature.tags:
#        context.server.shutdown()
#        context.thread.join()
#        context.browser.quit()

#def after_feature(context, feature):
#    print("after_feature")
#    global n
#    global users
#    #    n = int(number.strip())
#    #    if n <= len(users):
#    user = users[n]
#    print("User: %s" % (user))
#    res = rest.deleteMyselfFromSpotbot(access_token, user["pin"])
#    print("Status code: %s" % res.status_code)
#    assert  res.status_code == 200
#
#def before_all(context):
#    print("before_all")
#    global n
#    global users
#    #    n = int(number.strip())
#    #    if n <= len(users):
#    user = users[n]
#    print("User: %s" % (user))
#
#def after_all(context):
#    print("after_all")
#    global n
#    global users
#    #    n = int(number.strip())
#    #    if n <= len(users):
#    user = users[n]
#    print("User: %s" % (user))
#    res = rest.deleteMyselfFromSpotbot(access_token, user["pin"])
#    print("Status code: %s" % res.status_code)
#    assert  res.status_code == 200