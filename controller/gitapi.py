# Code taken from https://github.com/softdevteam/mattermost-github-integration to integrate
# into hvo-api, which was already running

from flask import request, current_app
from flask_restful import Resource
from model.gitdata import PullRequest, PullRequestComment, Issue, IssueComment, Repository, Branch, Push, Tag, CommitComment, Wiki
from logging import getLogger

import json
import urllib
import urllib2

class GitAPI(Resource):
    def __init__(self):
        super(GitAPI, self).__init__()

    def post(self):
        lf     = getLogger('file')
        if request.json is None:
            lf.debug('GitAPI::Invalid Content-Type')
            return 'Content-Type must be application/json and the request body must contain valid JSON', 400

        data  = request.json
        event = request.headers['X-Github-Event']

        msg = ""
        if event == "ping":
            msg = "ping from %s" % data['repository']['full_name']
        elif event == "pull_request":
            if data['action'] == "opened":
                msg = PullRequest(data).opened()
            elif data['action'] == "closed":
                msg = PullRequest(data).closed()
            elif data['action'] == "assigned":
                msg = PullRequest(data).assigned()
        elif event == "issues":
            if data['action'] == "opened":
                msg = Issue(data).opened()
            elif data['action'] == "closed":
                msg = Issue(data).closed()
            elif data['action'] == "labeled":
                msg = Issue(data).labeled()
            elif data['action'] == "assigned":
                msg = Issue(data).assigned()
        elif event == "issue_comment":
            if data['action'] == "created":
                msg = IssueComment(data).created()
        elif event == "repository":
            if data['action'] == "created":
                msg = Repository(data).created()
        elif event == "create":
            if data['ref_type'] == "branch":
                msg = Branch(data).created()
            elif data['ref_type'] == "tag":
                msg = Tag(data).created()
        elif event == "delete":
            if data['ref_type'] == "branch":
                msg = Branch(data).deleted()
        elif event == "pull_request_review_comment":
            if data['action'] == "created":
                msg = PullRequestComment(data).created()
        elif event == "push":
            if not (data['deleted'] and data['forced']):
                if not data['ref'].startswith("refs/tags/"):
                    msg = Push(data).commits()
        elif event == "commit_comment":
            if data['action'] == "created":
                msg = CommitComment(data).created()
        elif event == "gollum":
            msg = Wiki(data).updated()

        if msg:
            hook_info = get_hook_info(data)
            if hook_info:
                url, channel = get_hook_info(data)

                if hasattr(current_app.config, "GITHUB_IGNORE_ACTIONS") and \
                   event in current_app.config.GITHUB_IGNORE_ACTIONS and \
                   data['action'] in current_app.config.GITHUB_IGNORE_ACTIONS[event]:
                    return "Notification action ignored (as per configuration)"

                send_to_mattermost(msg, url, channel)
                return "Notification successfully posted to Mattermost", 201
            else:
                return "Notification ignored (repository is blacklisted).", 200
        else:
            return "Not implemented", 400

    def send_to_mattermost(text, url, channel):
        data             = {}
        data['text']     = text
        data['channel']  = channel
        data['username'] = current_app.config.GIT_USERNAME
        data['icon_url'] = current_app.config.GIT_ICON_URL

        headers  = {'Content-Type': 'application/json'}
        vals     = urllib.urlencode(data)
        req      = urllib2.Request(url, vals, headers)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            lf.debug("Error posting to Mattermost url: %s" % url)

    def get_hook_info(data):
        if 'repository' in data:
            repo = data['repository']['full_name']
            if repo in current_app.config.MATTERMOST_WEBHOOK_URLS:
                return current_app.config.MATTERMOST_WEBHOOK_URLS[repo]
        if 'organization' in data:
            org = data['organization']['login']
            if org in current_app.config.MATTERMOST_WEBHOOK_URLS:
                return current_app.config.MATTERMOST_WEBHOOK_URLS[org]
        if 'repository' in data:
            if 'login' in data['repository']['owner']:
                owner = data['repository']['owner']['login']
                if owner in current_app.config.MATTERMOST_WEBHOOK_URLS:
                    return current_app.config.MATTERMOST_WEBHOOK_URLS[owner]
            if 'name' in data['repository']['owner']:
                owner = data['repository']['owner']['name']
                if owner in current_app.config.MATTERMOST_WEBHOOK_URLS:
                    return current_app.config.MATTERMOST_WEBHOOK_URLS[owner]
        return current_app.config.MATTERMOST_WEBHOOK_URLS['default']
