const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'app.js'),'utf8');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'questions.json'),'utf8'));
const audit=JSON.parse(fs.readFileSync(path.join(root,'reports/question-catalog-audit.json'),'utf8'));
function app(initial={}){
 const data=new Map(Object.entries(initial)),writes=[];
 const nodes=new Map();
 const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',dataset:{},setAttribute(){},addEventListener(){},classList:{toggle(){}},click(){}});return nodes.get(id)};
 const localStorage={getItem:k=>data.has(k)?data.get(k):null,setItem:(k,v)=>{writes.push([k,String(v)]);data.set(k,String(v))},key:i=>[...data.keys()][i]??null,get length(){return data.size}};
 const context=vm.createContext({localStorage,document:{getElementById:node,querySelectorAll:()=>[],querySelector:()=>node('meta'),documentElement:{dataset:{}},addEventListener(){},createElement:()=>node('download')},navigator:{},location:{protocol:'http:'},window:{scrollTo(){}},fetch:()=>new Promise(()=>{}),confirm:()=>true,Blob,URL,setTimeout,console});
 vm.runInContext(source,context);
 vm.runInContext('QUESTIONS='+JSON.stringify(catalog),context);
 return {context,data,writes,run:code=>vm.runInContext(code,context),json:code=>JSON.parse(vm.runInContext('JSON.stringify('+code+')',context))};
}
function fixture(){
 const attempts=audit.baseline.questions.flatMap(q=>[
  {id:q.id,date:'2026-11-07T10:00:00Z',selected:[...q.answers],full:true,points:1,mode:'train'},
  {id:q.id,date:'2026-11-08T11:00:00Z',selected:[...q.answers],full:true,points:1,mode:'exam'},
  {id:q.id,date:'2026-11-08T11:01:00Z',selected:[],full:false,points:0,mode:'train'}]);
 return {attempts,notes:{'67':'Meine Notiz'},settings:{goal:20,custom:false},readIds:audit.baseline.questions.map(q=>q.id),futureField:{keep:['exact',1,null]},exams:[{id:'external-legacy',points:42.5,finished:true}]};
}
test('Update reads all legacy data without writing or reassessing it',()=>{
 const db=fixture(),raw=JSON.stringify(db),a=app({'gbu-study-v1':raw,'gbu-color-theme':'light','gbu-last-answer-order:67':'[3,1,0,2]','unrelated':'private'});
 assert.deepEqual(a.json('db'),db);assert.equal(a.data.get('gbu-study-v1'),raw);assert.equal(a.writes.length,0);
 assert.equal(a.run('masteredCount()'),273);
 for(const old of audit.baseline.questions){assert.equal(a.run(`mastered(QUESTIONS.find(q=>q.id===${old.id}))`),true);assert.equal(a.run(`attempts(${old.id}).length`),3)}
 for(const change of audit.changes.filter(c=>c.kind==='Ergänzung')){
  assert.equal(a.run(`attempts(${change.newId}).length`),0);assert.equal(a.run(`mastered(QUESTIONS.find(q=>q.id===${change.newId}))`),false);assert.equal(a.run(`readerProgress().includes(${change.newId})`),false);
 }
 a.run('stats()');assert.deepEqual(a.json('db'),db);assert.equal(a.writes.length,0);
 assert.equal(a.run("db.attempts.filter(x=>x.mode==='exam').length"),273);
 // Saving a later legitimate event preserves every old record and unknown field.
 a.run('markRead(277)');const saved=JSON.parse(a.data.get('gbu-study-v1'));
 assert.deepEqual(saved.attempts,db.attempts);assert.deepEqual(saved.exams,db.exams);assert.deepEqual(saved.futureField,db.futureField);assert.deepEqual(saved.notes,db.notes);assert.deepEqual(saved.settings,db.settings);
 assert.deepEqual(saved.readIds,[...db.readIds,277]);
});
test('Corrected IDs, answer positions and historical scores are stable',()=>{
 const a=app({'gbu-study-v1':JSON.stringify(fixture())});
 assert.equal(a.run('QUESTIONS.find(q=>q.id===67).answers[0]'),2);
 assert.equal(a.run('db.attempts.find(x=>x.id===67).points'),1);
 assert.deepEqual(a.json('db.attempts.find(x=>x.id===67).selected'),[3]);
 const before=new Map(audit.baseline.questions.map(q=>[q.id,q]));
 for(const q of catalog.filter(q=>before.has(q.id))){assert.deepEqual(q.options,before.get(q.id).options);assert.equal(q.chapter,before.get(q.id).chapter)}
});
test('All eligible questions and every selection follow the original partial-credit formula',()=>{
 const a=app();
 for(const q of catalog.filter(q=>a.run(`valid(QUESTIONS.find(q=>q.id===${q.id}))`))){
  for(let mask=0;mask<16;mask++){
   const selected=[0,1,2,3].filter(i=>mask&(1<<i));
   const right=selected.filter(i=>q.answers.includes(i)).length,wrong=selected.length-right;
   const expected=Math.max(0,right/q.answers.length-wrong/(4-q.answers.length));
   const actual=a.run(`score(QUESTIONS.find(q=>q.id===${q.id}),${JSON.stringify(selected)})`);
   assert.ok(Math.abs(actual-expected)<1e-12,`#${q.id}, mask ${mask}`);
  }
 }
 for(const count of [1,2,3]){
  const q={id:99999,text:'Test',options:['A','B','C','D'],answers:[0,1,2].slice(0,count),correctCount:count,flags:[]};
  a.run('testQuestion='+JSON.stringify(q));assert.equal(a.run('score(testQuestion,[])'),0);assert.equal(a.run('score(testQuestion,testQuestion.answers)'),1);assert.equal(a.run('score(testQuestion,[0,1,2,3])'),0);
 }
});
test('Malformed and unresolved questions never enter training or examination',()=>{
 const a=app();const base={text:'Test',options:['a','b','c','d'],answers:[0],correctCount:1,flags:[]};
 for(const patch of [{answers:[],correctCount:0},{answers:[0,1,2,3],correctCount:4},{answers:[-1]},{answers:[1.2]},{answers:[4]},{answers:[0,0],correctCount:2},{correctCount:2},{assessmentStatus:'unresolved'},{contextWarning:'unklar'},{flags:['nicht automatisch benoten']},{options:['a','','c','d']}]){
  a.run('testQuestion='+JSON.stringify({...base,...patch}));assert.equal(a.run('valid(testQuestion)'),false);assert.throws(()=>a.run('score(testQuestion,[])'));
 }
 a.run('testQuestion='+JSON.stringify(base));for(const selected of [[0,0],[-1],[4],[1.5]])assert.throws(()=>a.run('score(testQuestion,'+JSON.stringify(selected)+')'));
 a.run('startTrain("random")');assert.equal(a.run('session.list.every(valid)'),true);
 a.run('startExam()');assert.equal(a.run('session.list.length'),48);assert.equal(a.run('session.list.every(valid)'),true);
 for(const c of new Set(catalog.map(q=>q.chapter)))assert.equal(a.run(`session.list.filter(q=>q.chapter===${JSON.stringify(c)}).length`),4);
 assert.equal(a.run('session.list.some(q=>q.assessmentStatus==="unresolved")'),false);
});
test('Randomization preserves IDs, original indices, key, and score',()=>{
 const a=app();
 for(const q of catalog){
  a.run('testQuestion='+JSON.stringify(q));const saved=JSON.stringify(q);let previous=null;
  for(let k=0;k<4;k++){
   const order=a.json('newOrder(testQuestion)');assert.deepEqual([...order].sort((x,y)=>x-y),q.options.map((_,i)=>i));if(previous)assert.notDeepEqual(order,previous);previous=order;
   assert.equal(a.run('JSON.stringify(testQuestion)'),saved);
   if(a.run('valid(testQuestion)'))assert.equal(a.run('score(testQuestion,testQuestion.answers)'),1);
  }
 }
 assert.equal(a.data.has('gbu-study-v1'),false);
});
test('Full export is read-only, includes all DB fields and exact storage values',()=>{
 const db=fixture(),initial={'gbu-study-v1':JSON.stringify(db),'gbu-color-theme':'light','gbu-last-answer-order:67':'[2,1,3,0]','unrelated-token':'do-not-export'};
 const a=app(initial),before=[...a.data];const backup=a.json('backupData()');
 assert.deepEqual(backup.attempts,db.attempts);assert.deepEqual(backup.notes,db.notes);assert.deepEqual(backup.settings,db.settings);assert.deepEqual(backup.readIds,db.readIds);assert.deepEqual(backup.futureField,db.futureField);assert.deepEqual(backup.exams,db.exams);
 assert.equal(backup.schemaVersion,1);assert.equal(backup.backup.version,2);assert.equal(backup.backup.storage['gbu-study-v1'],initial['gbu-study-v1']);assert.equal(backup.backup.storage['gbu-color-theme'],'light');assert.equal(backup.backup.storage['gbu-last-answer-order:67'],'[2,1,3,0]');assert.equal(backup.backup.storage['unrelated-token'],undefined);
 assert.deepEqual([...a.data],before);assert.equal(a.writes.length,0);
});
test('New attempts snapshot the current corrected key without changing old attempts',()=>{
 const db=fixture(),a=app({'gbu-study-v1':JSON.stringify(db)});
 a.run('session={type:"train",list:[QUESTIONS.find(q=>q.id===67)],index:0,selected:[2],submitted:false,results:[],order:[0,1,2,3]}; next()');
 const saved=JSON.parse(a.data.get('gbu-study-v1'));assert.deepEqual(saved.attempts.slice(0,-1),db.attempts);
 const last=saved.attempts.at(-1);assert.equal(last.id,67);assert.equal(last.points,1);assert.equal(last.full,true);assert.deepEqual(last.answerKey,[2]);assert.equal(last.correctCount,1);assert.equal(last.questionRevision,'audit-2026-11-10');
});
test('Complete audit covers immutable import and all new questions exactly once',()=>{
 const raw=JSON.parse(fs.readFileSync(path.join(root,audit.sources.import.path),'utf8')).questions;
 assert.equal(audit.questions.length,raw.length);const ids=new Set();
 audit.questions.forEach((r,i)=>{assert.equal(r.importIndex,i+1);assert.deepEqual(r.raw,raw[i]);assert.ok('ABCDEF'.includes(r.category));if(r.newId){assert.equal(ids.has(r.newId),false);ids.add(r.newId)}});
 assert.deepEqual([...ids].sort((x,y)=>x-y),[274,275,276,277,278]);
});
test('Service worker refresh targets only its own file cache and retains the storage architecture',async()=>{
 const handlers={},deleted=[],opened=[];
 const context=vm.createContext({self:{skipWaiting(){},clients:{claim(){}},addEventListener:(event,fn)=>{handlers[event]=fn}},caches:{keys:async()=>['gbu-public-1','other-app-cache','gbu-public-audit-2026-11-10'],delete:async key=>{deleted.push(key)},open:async key=>{opened.push(key);return {addAll:async assets=>{assert.ok(assets.includes('./app.js?v=audit-2026-11-10'))}}}}});
 vm.runInContext(fs.readFileSync(path.join(root,'sw.js'),'utf8'),context);
 let pending;handlers.install({waitUntil:p=>{pending=p}});await pending;
 handlers.activate({waitUntil:p=>{pending=p}});await pending;
 assert.deepEqual(deleted,['gbu-public-1']);assert.deepEqual(opened,['gbu-public-audit-2026-11-10']);
 assert.ok(fs.readFileSync(path.join(root,'index.html'),'utf8').includes('app.js?v=audit-2026-11-10'));
});
