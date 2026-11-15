#!/usr/bin/env python3
"""A small local-first task list stored in a JSON file."""
import argparse,json,os,pathlib,sys,tempfile,unittest
def load_tasks(path):
    p=pathlib.Path(path)
    if not p.exists(): return []
    data=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data,list): raise ValueError("task file must contain a JSON list")
    return data
def save_tasks(path,tasks):
    p=pathlib.Path(path).expanduser(); p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=p.name+".",dir=p.parent,text=True)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream: json.dump(tasks,stream,ensure_ascii=False,indent=2); stream.write("\n")
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def add_task(tasks,text):
    if not text.strip(): raise ValueError("task text cannot be empty")
    next_id=max((int(t["id"]) for t in tasks),default=0)+1
    return tasks+[{"id":next_id,"text":text.strip(),"done":False}]
def complete_task(tasks,task_id):
    updated=False
    for task in tasks:
        if task["id"]==task_id: task["done"]=True; updated=True
    if not updated: raise ValueError(f"task {task_id} not found")
    return tasks
class Tests(unittest.TestCase):
    def test_add_and_complete(self):
        rows=add_task([],"Ship it"); self.assertEqual(rows[0]["id"],1)
        self.assertTrue(complete_task(rows,1)[0]["done"])
    def test_blank_rejected(self):
        with self.assertRaises(ValueError): add_task([],"  ")
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--file",default="~/.taskshelf.json")
    sub=ap.add_subparsers(dest="command",required=True); add=sub.add_parser("add"); add.add_argument("text")
    sub.add_parser("list"); done=sub.add_parser("done"); done.add_argument("id",type=int); a=ap.parse_args(); path=pathlib.Path(a.file).expanduser()
    try:
        rows=load_tasks(path)
        if a.command=="add": rows=add_task(rows,a.text); save_tasks(path,rows); print(f"Added task {rows[-1]['id']}.")
        elif a.command=="done": rows=complete_task(rows,a.id); save_tasks(path,rows); print(f"Completed task {a.id}.")
        else:
            for t in rows: print(f"[{'x' if t['done'] else ' '}] {t['id']:>3}  {t['text']}")
            if not rows: print("No tasks yet. Add one with: python tool.py add \"Your task\"")
    except (OSError,ValueError,json.JSONDecodeError) as exc: ap.error(str(exc))
if __name__=="__main__":
    if "--self-test" in sys.argv: unittest.main(argv=[sys.argv[0]])
    else: main()
