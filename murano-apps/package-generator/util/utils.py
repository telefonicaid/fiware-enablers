__author__ = 'henar'
import os
import sys
import git
import urllib

COOKBOOK_FOLDER ="cookbooks/"
def replace_word(infile,old_word,new_word):
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)

    f1=open(infile,'r').read()
    f2=open(infile,'w')
    m=f1.replace(old_word,new_word)
    f2.write(m)
    f2.close()

def is_git_repository( url):
    return (url.startswith(("git://",
                            "git+http://", "git+https:/"))
            or url.endswith('.git'))

def get_name_folder(url):
    end = url.rsplit('/', 1)[1]
    if ".git" in end:
        return end[0:end.find(".git")]
    return end

def read_metadata(url_file):
    print url_file
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

