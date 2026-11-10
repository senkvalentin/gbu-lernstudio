import fitz,re,json,collections
p=fitz.open('/mnt/data/betriebs-u-fragen.pdf')
lines=[]
for pi,page in enumerate(p):
 for s in page.get_text().splitlines():
  s=s.strip()
  if s: lines.append((pi+1,s))
qpat=re.compile(r'\(([123])\)\s*$')
optpat=re.compile(r'^([1-5])\.\s*(.*)$')
anspat=re.compile(r'^(?:[1-5]\s*(?:&|,|und|\+)\s*)*[1-5](?:\s*\([^)]*\))?\s*$',re.I)
questions=[]; i=0; topic='Allgemein'
while i<len(lines):
 page,s=lines[i]
 # header if not question and no numbering
 if len(s)<65 and not re.search(r'[.!?]$',s) and s in ['Logistik-Management','Qualitätsmanagement','Absatzmanagement','Unternehmenskooperation','Personalmanagement','Finanzmanagement','Produktionsmanagement','Controlling','Strategisches Management','Organisation','Marketing','Investition','Finanzierung','Kostenrechnung','Innovationsmanagement','Nachhaltigkeit']:
  topic=s
 if qpat.search(s):
  k=int(qpat.search(s).group(1)); question=s; j=i+1
  while j<len(lines) and j<i+4 and not optpat.match(lines[j][1]):
   question+=' '+lines[j][1];j+=1
  opts=[]
  while j<len(lines) and len(opts)<5:
   m=optpat.match(lines[j][1])
   if not m or int(m.group(1))!=len(opts)+1: break
   opt=m.group(2);j+=1
   while j<len(lines) and not optpat.match(lines[j][1]) and not anspat.match(lines[j][1]) and not qpat.search(lines[j][1]) and len(opt)<600:
    opt+=' '+lines[j][1];j+=1
   opts.append(opt.strip())
  if len(opts)>=4:
   answer=[]; answer_line='';
   if j<len(lines) and anspat.match(lines[j][1]):
    answer_line=lines[j][1];answer=[int(v)-1 for v in re.findall(r'[1-5]',answer_line)];j+=1
   explanation=[]
   while j<len(lines) and not qpat.search(lines[j][1]) and j-i<65:
    if len(' '.join(explanation))<1800: explanation.append(lines[j][1]);
    j+=1
   flags=[]
   if len(opts)!=4:flags.append('Abweichende Anzahl Antwortmöglichkeiten')
   if not answer:flags.append('Kein Lösungsschlüssel erkannt')
   if answer and len(answer)!=k:flags.append('Lösungsschlüssel weicht von angegebener Anzahl ab')
   if any(x>=len(opts) for x in answer):flags.append('Lösung außerhalb der Optionen')
   if any(v in ('[?]','[??]') for v in opts):flags.append('Unsichere Originalformulierung')
   if 'edit ' in ' '.join(explanation).lower() or 'achtung' in ' '.join(explanation).lower() or 'falsch' in answer_line.lower():flags.append('Kommentar oder Korrektur im Katalog prüfen')
   chapter=next((name for start,name in reversed([(1,'Produktion'),(6,'Logistik'),(12,'Qualitätsmanagement'),(19,'Absatzmanagement'),(26,'Innovationsmanagement'),(30,'Strategisches Management'),(37,'Kosten- und Erfolgsrechnung'),(45,'Finanzmanagement'),(50,'Organisation'),(56,'Personalmanagement'),(61,'Unternehmenskooperation'),(69,'Weitere Themen / Nachhaltigkeit')]) if page>=start),'Sonstiges')
   questions.append(dict(id=len(questions)+1,chapter=chapter,page=page,text=re.sub(r'\s*\([123]\)\s*$','',question).strip(),correctCount=k,options=opts,answers=answer,sourceAnswer=answer_line,explanation=' '.join(explanation).strip()[:1800],flags=flags))
   i=j;continue
 i+=1
with open('/mnt/data/gbu-lernapp/questions.json','w') as f:json.dump(questions,f,ensure_ascii=False)
print('questions',len(questions),'flagged',sum(bool(x['flags']) for x in questions),'topics',collections.Counter(x['chapter'] for x in questions))
print('first',questions[0]);print('last',questions[-1]['text'][:100]);
