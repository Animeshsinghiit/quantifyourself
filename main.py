from flask import Flask,render_template,request,redirect,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
app=Flask(__name__)
app.debug=True
db=SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
app.config['SECRET_KEY']='Q323424'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String,unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    email=db.Column(db.String,unique=True, nullable=False)
    trackers=db.relationship('tracker',backref='user',lazy=True,cascade='all,delete')
class tracker(db.Model):
    t_id=db.Column(db.Integer, primary_key=True)
    Name=db.Column(db.String,nullable=False)
    desc=db.Column(db.String,nullable=False)
    type=db.Column(db.String)
    Settings=db.Column(db.String)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'))
    logs=db.relationship('Addlog',backref='tracker',lazy=True,uselist=False,cascade='all,delete')
class Addlog(db.Model):
    log_id=db.Column(db.Integer,primary_key=True)
    when=db.Column(db.String)
    value=db.Column(db.String)
    notes=db.Column(db.String)
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.t_id',ondelete='CASCADE'),nullable=False)
@app.route('/')
def Index():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('login.html')
# Registration form
@app.route('/register',methods=['GET','POST'])
def Register():
    if request.method=='POST':
        username=request.form.get("user")
        password=request.form.get("pswd")
        email=request.form.get("email")
        user1=User.query.filter_by(username=username).first()
        if user1==None:
            new=User(username=username,password=password,email=email)
            db.session.add(new)
            db.session.commit()
            return redirect('/')
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('registration.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=request.form.get('user')
        pswd=request.form.get('pswd')
        session['username']=user
        session['password']=pswd
        e_user=User.query.filter_by(username=user).first_or_404(description='There is no user with username {}'.format(user))
        # print(e_user)
        if e_user.password==pswd:
            return redirect('/dashboard')
    return redirect('/dashboard')
@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('password',None)
    return redirect('/')
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        u1=User.query.filter_by(username=session['username']).first()
        t1=tracker.query.filter_by(user_id=u1.id)
        return render_template('dashboard.html', track=t1,rev=rev)
    else:
        return redirect('/')
# new tracker
@app.route('/addtracker/<user1>',methods=['GET','POST'])
def addtracker(user1):
    if request.method=='POST':
        tname=request.form.get('tname')
        desc=request.form.get('desc')
        type=request.form.get('type')
        sett=request.form.get('sett')
        user1=User.query.filter_by(username=session['username']).first()
        u_id=user1.id
        t1=tracker(Name=tname,desc=desc,type=type,Settings=sett,user_id=u_id)
        db.session.add(t1)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('tracker.html')
# updating tracker
@app.route('/update/<int:t_id>',methods=['GET','POST'])
def update(t_id):
    if request.method=='POST':
        Name=request.form.get('tname')
        desc=request.form.get('desc')
        type=request.form.get('type')
        sett=request.form.get('sett')
        t1=tracker.query.filter_by(t_id=t_id).first()
        t1.Name=Name
        t1.desc=desc
        t1.type=type
        t1.Settings=sett
        db.session.add(t1)
        db.session.commit()
        return redirect('/')
    t1=tracker.query.get(t_id)
    return render_template('update_tracker.html',t1=t1)


# delete function
@app.route('/del_track/<int:t_id>',methods=['POST','GET'])
def del_track(t_id):
    l1=Addlog.query.filter_by(tracker_id=t_id).delete()
    t1=tracker.query.filter_by(t_id=t_id).first()
    db.session.delete(t1)
    db.session.commit()
    return redirect('/')   

# add log to tracker
@app.route('/addlog/<int:t_id>',methods=['POST','GET'])
def addlog(t_id):
    type=tracker.query.filter_by(t_id=t_id).first()
    type=type.type
    print(type)
    setting=tracker.query.filter_by(t_id=t_id).first()
    setting=setting.Settings
    opt_list=list(setting.split(","))
    print(opt_list)
    if request.method=='POST':
        value=request.form.get('value')
        note=request.form.get('note')
        log1=Addlog(value=value,notes=note,tracker_id=t_id,when=datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
        db.session.add(log1)
        db.session.commit()
        return redirect('/')
    return render_template('mytracker.html',id=t_id,type=type,opt=opt_list)
rev=""
@app.route('/track/<int:trackid>')
def track(trackid):
    global rev
    rev=datetime.now().strftime("%d/%m/%Y,%H:%M")
    track1=tracker.query.filter_by(t_id=trackid).first()
    log1=Addlog.query.filter_by(tracker_id=trackid).all()
    return render_template('track.html',log1=log1,track1=track1)
@app.route('/updatetrack/<int:id>/<int:tid>',methods=['POST','GET'])
def updatetrack(id,tid):
    type=tracker.query.filter_by(t_id=tid).first()
    type=type.type
    print(type)
    setting=tracker.query.filter_by(t_id=tid).first()
    setting=setting.Settings
    opt_list=list(setting.split(",")) 
    if request.method=='POST':
        value=request.form.get('value')
        note=request.form.get('note')
        log1=Addlog.query.filter_by(log_id=id).first()
        log1.value=value
        log1.notes=note
        db.session.add(log1)
        db.session.commit()
        return redirect('/track/'+str(tid))
    item=Addlog.query.filter_by(log_id=id).first()
    # track1=tracker.query.filter_by(t_id=tid).first()
    return render_template('updatelog.html',item=item,tid=tid,type=type,opt=opt_list)
    
    
@app.route('/deletetrack/<int:id>/<int:tid>')
def deletetrack(id,tid):
    item=Addlog.query.filter_by(log_id=id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect('/track/'+str(tid))
@app.route('/chart')
def chart():
    return render_template('chart.html')
@app.route('/graph/<int:t_id>')
def graph(t_id):
    t1=tracker.query.get(t_id)
    if t1.type=="num":
        logs=Addlog.query.filter_by(tracker_id=t_id).all()
        y_axis=[]
        x_axis=[]
        for i in logs:
            y_axis.append(int(i.value))
        for i in logs:
            x_axis.append(i.when[:10])
        return render_template('graph.html',labels=x_axis,values=y_axis,t_id=t_id)
    

    

if __name__=='__main__':
    app.run(debug=True)
