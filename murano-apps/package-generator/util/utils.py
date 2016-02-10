#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
import os
import sys
import git
import urllib

COOKBOOK_FOLDER ="cookbooks/"
def replace_word(infile,old_word,new_word):
    """
    It replace a word in a file.
    :param infile: the file
    :param old_word: old word
    :param new_word: the work to replace
    """
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)

    f1=open(infile,'r').read()
    f2=open(infile,'w')
    m=f1.replace(old_word,new_word)
    f2.write(m)
    f2.close()

def is_git_repository( url):
    """
    It returns if the url is a git repository.
    :param url:
    :return: True/False
    """
    return (url.startswith(("git://",
                            "git+http://", "git+https:/"))
            or url.endswith('.git'))

def get_name_folder(url):
    """
    It returns the name of the folder for the url repository.
    :param url:
    :return:
    """
    end = url.rsplit('/', 1)[1]
    if ".git" in end:
        return end[0:end.find(".git")]
    return end

def read_metadata(url_file):
    """
    It reads the metadata.rb from a git or svn repository .
    :param url_file:
    :return: the metadata.rb in string
    """
    metadata_str = ''

    if not os.path.exists(COOKBOOK_FOLDER):
        os.makedirs(COOKBOOK_FOLDER)
    folder = COOKBOOK_FOLDER + get_name_folder(url_file)
    if is_git_repository(url_file):
        if not os.path.exists(folder):
            git.Git().clone(url_file, folder)
        if os.path.exists(folder + "/metadata.rb"):
            infile = open(folder + "/metadata.rb", 'r')
            metadata_str = infile.read()

    else:
        f = urllib.urlopen(url_file+"/metadata.rb")
        metadata_str = f.read()
    return metadata_str

