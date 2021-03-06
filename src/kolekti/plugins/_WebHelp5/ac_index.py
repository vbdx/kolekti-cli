# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re

class indexer:
    def __init__(self):
        # init with (ab,b)
        # 0
        # a --- b
        # b
        self.nodes=['']
        self.nexts=[0]
        self.child=[0]
        self.terms=[{}]
        self.wordcount={}

    def newnode(self, letter):
        self.nodes.append(letter)
        self.nexts.append(0)
        self.child.append(0)
        self.terms.append({})
        return len(self.nodes)-1

    def addword(self,word, ref):
        index=self.nodes[0]
        parent=0
        for letter in word:
            cnode=self.child[parent]
            if cnode==0:
                # no child, create the first one !
                new=self.newnode(letter)
                self.child[parent]=new
                parent=new
                continue

            lastnode=0
            while cnode != 0 and letter != self.nodes[cnode]:
                lastnode=cnode
                cnode=self.nexts[cnode]

            # end of nodes (cur char not found) link a new node at end of next list
            if cnode==0:
                new=self.newnode(letter)
                self.nexts[lastnode]=new
                cnode=new
            parent=cnode
        if self.terms[parent].has_key(ref):
            self.terms[parent][ref]=self.terms[parent][ref]+1
        else:
            self.terms[parent][ref]=1
        if self.wordcount.has_key(ref):
            self.wordcount[ref]=self.wordcount[ref]+1
        else:
            self.wordcount[ref]=1

    def writewords(self):
        s="var nodes=%s;"%re.sub(", u",',',str(self.nodes))
        s=s+"var nexts=%s;"%str(self.nexts)
        s=s+"var child=%s;"%str(self.child)
        s=s+"var terms=%s;"%str(self.terms)
        s=s+"var wordcount=%s;"%str(self.wordcount)
        return s



excludes=['de','la','qui','ou','un']
trsl=u'                                                0123456789       abcdefghijklmnopqrstuvwxyz      abcdefghijklmnopqrstuvwxyz                                                                                                                                     '
rep_in=u"àâäéèêëïîôöùûç\u2019"
rep_out="aaaeeeeiioouuc "

def lexer(text):
    res=[]
    # downcase texte
    t=text
    t=t.lower()
    # remplace les caractères accentués dans texte
    for l in range(len(rep_in)):
        t=re.sub(rep_in[l],rep_out[l],t)
    t=t.translate(trsl)
    for w in t.split():
        if len(w) > 2:
            if not w in res and not w in excludes:
                res.append(w)
    return res
