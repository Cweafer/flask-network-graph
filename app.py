import praw
from flask import Flask, render_template, request
from forms import SearchForm

app = Flask(__name__)

#Enter your Reddit appliation's credentials below.
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
USER_AGENT = ''
reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI,user_agent=USER_AGENT)

@app.route('/', methods=['GET', 'POST'])
def main():
    errors = []
    form = SearchForm2(request.form)
    if request.method == "POST" and form.validate():
        submission = None
        if form.data['submission_id'].startswith("www") or form.data['submission_id'].startswith("http"):
            submission = reddit.submission(url=form.data['submission_id'])
        else:
            submission = reddit.submission(id=form.data['submission_id'])
        try:
            all_submission_comments = list(submission.comments)
            all_submission_comments = submission.comments.list()

            all_comments = []
            finished_authors = []
            data = {}
            data['_id'] = submission.name
            data['author'] = str(submission.author)
            all_comments.append(data)
            for comment in all_submission_comments:
                #checks if we're iterating over a comment and not a more comment
                if isinstance(comment, MoreComments) or str(comment.author) == "None":
                    continue
                data = {}
                data['_id'] = comment.name
                data['parent_id'] = comment.parent_id
                data['author'] = str(comment.author)
                all_comments.append(data)

            ids_to_names = {}
            for comment in all_comments:
                if 'parent_id' in comment:
                    for comment2 in all_comments:
                        if comment['parent_id'] == comment2['_id']:
                            ids_to_names[str(comment2['_id'])] = str(comment2['author'])

            nodes = []
            edges = []
            finished_authors = []
            for idx, comment in enumerate(all_comments):
                if comment['author'] == "None" or comment['author'] in finished_authors:
                    continue
                color, size = None, None
                if idx == 0:
                    color = "rgb(0,0,150)"
                    size = 45
                elif comment['parent_id'] != all_comments[0]['_id']:
                    color = "rgb(0,150,150)"
                    size = 7
                else:
                    color = "rgb(0, 150,0)"
                    size = 15
                nodes.append({'id': comment['author'], "label": comment['author'], "color": color, "size": size, "x": idx*2, "y": -idx*2 })
                finished_authors.append(comment['author'])

            for idx, comment in enumerate(all_comments):
                if comment['author'] == "None" or ('parent_id' in comment and comment['parent_id'] not in ids_to_names) or ('parent_id' in comment and str(ids_to_names[comment['parent_id']]) == "None"):
                    continue
                color, size = None, None
                if idx == 0:
                    color = "rgb(0,0,150)"
                    size = 45
                elif comment['parent_id'] != all_comments[0]['_id']:
                    color = "rgb(0,150,150)"
                    size = 7
                else:
                    color = "rgb(0, 150,0)"
                    size = 15
                if 'parent_id' in comment:
                    edges.append({'id': comment['_id'], "source": comment['author'], "target": str(ids_to_names[comment['parent_id']])})

            json_data = {"nodes": nodes, "edges": edges}

        except Exception as ex:
            #print(ex)
            errors.append("Please enter a valid URL or submission ID!")
            return render_template('graph_start.html', form=form,errors=errors)


        return render_template('graph.html', form=form, json_data=json_data)
    return render_template('graph_start.html', form=form,errors=errors)

if __name__ == '__main__':
  app.run(debug= True,host="127.0.0.1",port=5000, threaded=True)
