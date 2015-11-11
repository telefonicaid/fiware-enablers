FIWARE Enablers
***************

This is a repository that contains the different scripts used to generated FIWARE GE(r)is images and/or their recipes.

The structure of the directory looks something like this:

 ::

     fiware-enablers
       ├───README.rst
       ├───images
       │   ├───README.rst
       │   ├───<GEri/GEi-name1>
       │   │   ├───4.4_create.sh
       |   |   ├───4.4_test.sh
       │   │   ├───5.1_create.sh
       │   │   ├───5.1_test.sh
       │   │   └───...
       │   ├───<GEri/GEi-name2>
       │   │   └───...
       │   └───...
       ├───chef-recipes
       │   ├───README.rst
       │   ├───<GEri/GEi-name1>
       │   │   ├───recipe_name1
       |   |   |   ├───README.rst
       |   |   |   ├───fiware_release
       |   |   |   ├───metadata.rb
       |   |   |   ├───attributes
       |   |   |   ├───templates
       |   |   |   ├───recipes
       |   |   |   |   ├───0.0.1_install.rb
       |   |   |   |   ├───0.0.1_uninstall.rb
       |   |   |   |   ├───0.1.2_install.rb
       |   |   |   |   ├───0.1.2_uninstall.rb
       |   |   |   |   └───...
       |   |   |   └───...
       │   │   ├───recipe_name2
       |   |   |   └───...
       │   │   └───...
       │   ├───<GEri/GEi-name2>
       │   │   └───...
       │   └───...
       ├───puppet-modules
       |   ├───README.rst
       |   ├───<GEri/GEi-name1>
       |   │   ├───module_name1
       |   |   |   ├───README.rst
       |   |   |   ├───fiware_release
       |   │   |   ├───files
       |   │   |   ├───templates
       |   │   |   ├───manifests
       |   │   |   |   ├───init.pp
       |   │   |   |   ├───install.pp
       |   │   |   |   ├───uninstall.pp
       |   │   |   |   └───...
       |   │   |   └───...
       |   |   ├───module_name2 
       |   │   |   └───...
       |   │   └───...
       |   ├───<GEri/GEi-name2>
       |   │   └───...
       |   └───...
       ├───murano-apps
       |   ├───README.rst
       |   ├───Chef
       |   │   ├───AppGEiName1Chef
       |   |   |   ├───README.rst
       |   |   |   ├───fiware_release
       |   |   |   ├───package
       |   |   |   |   ├───Classes
       |   │   |   |   |   └───...
       |   |   |   |   └───Resources
       |   │   |   |       └───...
       |   │   |   └───...
       |   │   └───...
       |   └───Puppet
       |       └───...
       |

   

An overview of what each of these does:

================  =============
 DIRECTORY         DESCRIPTION
================  =============
 images            Directory that contains the script used to create the Generic Enabler images.
 chef-recipes      Directory that contains the different chef recipes for all the Generic Enablers.
 puppet-modules    Directory that contains the different puppet modules for all the Generic Enablers.
 GEri/GEi-name1    Directory corresponding to each Generic Enabler (reference) instance.
================  =============

Pay attention that you should include a file named *fiware_release* in your Chef-Recipes and Puppet-Modules where you should
specify all information about the FIWARE Release of these software.

Last but not least, the repository is structured in branchs:

- master, stable version, at the end of a Release n, we make a pull request from Release n-1 in develop into master branch
  and we create a new tag with all stable content of the repo for that FIWARE release.
- develop, default work branch.
- feature/<GEri/GEi-name>, branch used by the GEri/GEi owner to upload the content.

How to contribute to this repo
==============================

Probably, you will not have access rights to create branches in this repo. If so, you must request them to FIWARE Lab team 
or work in your own forked repository.

To know what are 'Forks' and how you can use it for this repository, please take a look at the GitHub documentation: `Fork a Repo`_
Once you have this repo forked, you will be able to create branches in your own *fork* to upload your content. 
If you have requested access rights to this repo as developer, you will be able to create branches straight in the *fiware-enablers* repository.

Branches used by the GEri/GEi owner for contributing to the origin repo should have the format `feature/<GEri/GEi-name>`. 
When you consider that the scripts developed in your local branch are correct you should launch a pull request 
to *develop*. FIWARE Lab team will check the scripts in order to secure that 
they are working and if all is correct we will accept the pull request into *develop* branch.

If you are woking with *forks*, note that you must update your local repo with the latest changes when they are merged 
into *origin/develop*.


.. _Fork a Repo: https://help.github.com/articles/fork-a-repo/

