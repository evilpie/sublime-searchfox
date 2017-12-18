import sublime
import sublime_plugin

import urllib.request
import urllib.parse
import json

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

        window = sublime.active_window()

        def on_select(index):
            if index < 0:
                return

            item = items[index]
            print(item)

            path = item['line'][0]['path']
            # Todo: resolve this properly somehow
            full_path = window.project_data()['folders'][0]['path'] + '/' + path

            path_with_line = "{}:{}".format(full_path, item['line'][0]['lines'][0]['lno'])

            window.open_file(path_with_line, sublime.ENCODED_POSITION | sublime.TRANSIENT)

        window.show_quick_panel([[item['name'], item['line'][0]['path']] for item in items], on_select)
