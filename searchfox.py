# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sublime
import sublime_plugin

import urllib.request
import urllib.parse
import json
import os

# Copied from https://hg.mozilla.org/mozilla-central/file/5d203926da51a7e949a20818664b19d5b115572d/python/mozbuild/mozbuild/base.py

def ancestors(path):
    """Emit the parent directories of a path."""
    while path:
        yield path
        newpath = os.path.dirname(path)
        if newpath == path:
            break
        path = newpath

def find_top_srcdir(path):
    for dir_path in ancestors(path):
        # We choose an arbitrary file as an indicator that this is a
        # srcdir.
        our_path = os.path.join(dir_path, 'python', 'mozbuild', 'mozbuild', 'base.py')
        if os.path.isfile(our_path):
            return dir_path

class FindOnSearchfoxCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        region = view.sel()[0]
        if region.begin() == region.end():  # point
            region = view.word(region)
        symbol = view.substr(region)

        values = {'q': symbol}
        url = 'https://searchfox.org/mozilla-central/search?' + urllib.parse.urlencode(values)
        headers = {'Accept': 'text/json'}
        req = urllib.request.Request(url, None, headers)

        with urllib.request.urlopen(req) as response:
            string = response.read().decode('utf-8')
            data = json.loads(string)

        normal = data['normal']

        items = []
        for key in normal.keys():
            if 'Definition' in key:
                items.append({'name': key[13:-1], 'line': normal[key]})

        window = view.window()

        def on_select(index):
            if index < 0:
                return

            item = items[index]
            print(item)

            path = item['line'][0]['path']

            top_srcdic = find_top_srcdir(window.folders()[0])
            print(top_srcdic)

            full_path = os.path.join(top_srcdic, path)
            path_with_line = "{}:{}".format(full_path, item['line'][0]['lines'][0]['lno'])

            window.open_file(path_with_line, sublime.ENCODED_POSITION | sublime.TRANSIENT)

        window.show_quick_panel([[item['name'], item['line'][0]['path']] for item in items], on_select)
