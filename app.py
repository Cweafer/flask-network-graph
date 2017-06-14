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
    form = SearchForm(request.form)
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

            data = {}
            data['_id'] = submission.name
            all_comments.append(data)
            for comment in all_submission_comments:
                data = {}
                data['_id'] = comment.name
                data['parent_id'] = comment.parent_id
                all_comments.append(data)

            nodes = []
            edges = []
            for idx, comment in enumerate(all_comments):
                #error that occurred - sets the id's to "t1__" (can't think of why atm)
                if comment['_id'] != "t1__":
                    color, size = None, None
                    #Submission node
                    if idx == 0:
                        color = "rgb(0,0,150)"
                        size = 45
                    #Comments to comments
                    elif comment['parent_id'] != all_comments[0]['_id']:
                        color = "rgb(0,150,150)"
                        size = 7
                    #Comments to submission
                    else:
                        color = "rgb(0, 150,0)"
                        size = 15
                    nodes.append({'id': comment['_id'], "label": comment['_id'], "color": color, "size": size, "x": idx, "y": -idx, "type": "tweetegy" })
                    if 'parent_id' in comment:
                        edges.append({'id': comment['_id'], "source": comment['_id'], "target": comment['parent_id']})

            json_data = {"nodes": nodes, "edges": edges}

        except:
            errors.append("Please enter a valid URL or submission ID!")
            return render_template('index.html', form=form,errors=errors)

        return render_template('graph.html', form=form, json_data=json_data)
    return render_template('index.html', form=form,errors=errors)

if __name__ == '__main__':
  app.run(debug= True,host="127.0.0.1",port=5000, threaded=True)
