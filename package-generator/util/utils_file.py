#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Telefónica Investigación y Desarrollo, S.A.U
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
import urllib
from github import Github
from os import listdir
from os.path import join, isdir
import time
import git
from configuration import Config
import yaml


COOKBOOK_FOLDER = "cookbooks/"


def replace_word(infile, old_word, new_word):
    """
    It replace a word in a file.
    :param infile: the file
    :param old_word: old word
    :param new_word: the work to replace
    :return: nothing
    """
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)

    f1 = open(infile, 'r').read()
    f2 = open(infile, 'w')
    m = f1.replace(old_word, new_word)
    f2.write(m)
    f2.close()


def is_git_repository(url):
    """
    It returns if the url is a git repository.
    :param url: the url to check if it is a git repo
    :return: True/False
    """
    return (url.startswith(("git://",
                            "git+http://", "git+https:/"))
            or url.endswith('.git'))


def get_name_folder(url):
    """
    It returns the name of the folder for the url repository.
    :param url: the url to obtain the folder
    :return: folder
    """
    splits = url.rsplit('/', 1)
    if len(splits) == 1:
        return url
    end = splits[1]
    if ".git" in end:
        return end[0:end.find(".git")]
    return end


def read_metadata_puppet(url_file):
    """
    It reads the metadata.json from a git or svn repository .
    :param url_file: the url to obtain the metadata
    :return: the metadata in string
    """
    read_metadata(url_file, "metadata.json")


def read_metadata_chef(url_file):
    """
    It reads the metadata.rb from a git or svn repository .
    :param url_file: the url to obtain the metadata
    :return: the metadata in string
    """
    read_metadata(url_file, "metadata.rb")


def read_metadata(url_file, metadata_file):
    """
    It reads the metadata files for both Chef and Puppet
    :param url_file: the url to obtain the metadata
    :param metadata_file: the metadata file name
    :return: a string with the metadata contain
    """
    metadata_str = None
    try:
        if not os.path.exists(COOKBOOK_FOLDER):
            os.makedirs(COOKBOOK_FOLDER)
        folder = COOKBOOK_FOLDER + get_name_folder(url_file)
        if is_git_repository(url_file):
            download_files_git(url_file)
            if os.path.exists(folder + "/" + metadata_file):
                infile = open(folder + "/" + metadata_file, 'r')
                metadata_str = infile.read()
        else:
            f = urllib.urlopen(url_file + "/" + metadata_file)
            metadata_str = f.read()
    except:
        pass
    return metadata_str


def read_yaml_local_file(file):
    """
    It reads a yaml file and store in a dict.
    :param file: the file to read
    :return: dict
    """
    try:
        with open(file, "r") as fread:
            stream = fread.read()
            text = yaml.load(stream)
            fread.close()
    except:
        return None
    return text


def write_local_yaml(out_file, yaml_text):
    """
    It write a yaml file to a file
    :param out_file: the file where to store the data
    :param yaml_text: the file content
    :return: nothing
    """
    with open(out_file, 'w+') as fwrite:
        data = yaml.dump(yaml_text, default_flow_style=True)
        fwrite.write(data)
        fwrite.close()


def create_github_pull_request(repo_url, user_github, password_github, branch):
    """
    It creates a github pull request
    :param repo_url: the github repository
    :param user_github: the user github
    :param password_github: the password github
    :param branch: the branch
    """
    g = Github(user_github, password_github)
    for repo in g.get_user().get_repos():
        if repo.url == repo_url:
            repo.create_pull("New update in Murano-packages",
                             "Created by package-generator", "develop", branch)


def download_files_git(url_file):
    """
    It download a file repository
    :param url_file: the git repository url
    :return nothing
    """
    folder = COOKBOOK_FOLDER + get_name_folder(url_file)
    download_git_repo(url_file, folder)


def download_git_repo(url_file, folder):
    """
    It download a git repo in a folder
    :param url_file: the git repo url
    :param folder: the folder to download
    :return: nothing
    """
    if is_git_repository(url_file):
        if not os.path.exists(folder):
            git.Git().clone(url_file, folder)


def create_branch(folder):
    """
    It creates a branch in the git repo and upload it
    into github
    :param folder: The folder to create the brach.
    :return: the branch name
    """
    repo = git.repo.Repo(folder)
    str_branch = "update_packages"+str(time.time())

    # Create branch in repo
    new = repo.create_head(str_branch)
    files = [f for f in listdir("./../murano-apps")
             if isdir(join("./../murano-apps", f))]

    for folder in files:
        # add it to the index
        repo.index.add(["murano-apps/"+folder])

    repo.index.commit("Murano Packages update. "
                      "Ready to be merged")
    repo.commit()
    repo.remotes.origin.push(new)
    return str_branch


def delete_branch(branch):
    """
    It deletes the branch in the git repo
    :param branch: the branch to delete
    :return: nothing
    """
    repo = git.repo.Repo("./../")
    repo.delete_head(branch)
    repo.commit()


def get_murano_app_name(murano_app):
    """
    It gets the murano package name in the oficial repository.
    :return:
    """
    try:
        return Config.CONFIG_MURANOAPPS.get('main', murano_app)
    except:
        return None
