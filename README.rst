FIWARE Enablers
***************

This is a repository that contains the different scripts used to generated FIWARE GE(r)is images and/or their recipes.

The structure of the directory looks something like this:

 ::

    ├───README.rst
    │   ├───chef-recipes
    │   │   ├───README.rst
    │   │   ├───<GEri/GEi-name1>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   ├───<GEri/GEi-name2>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   └───...
    │   ├───images
    │   │   ├───README.rst
    │   │   ├───<GEri/GEi-name1>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   ├───<GEri/GEi-name2>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   └───...
    │   ├───puppet-modules
    │   │   ├───README.rst
    │   │   ├───<GEri/GEi-name1>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   ├───<GEri/GEi-name2>
    │   │   │   ├───Release4.4
    │   │   │   ├───Release5.1
    │   │   │   └───...
    │   │   └───...
    │   │
    │

An overview of what each of these does:

==================  =============
 FILE / DIRECTORY    DESCRIPTION
==================  =============
 chef-recipes        Directory that contains the different chef recipes for all the Generic Enablers.
 images              Directory that contains the script used to create the Generic Enabler images.
 puppet-modules      Directory that contains the different puppet modules for all the Generic Enablers.
 <GEri/GEi-name1>    Directory corresponding to each Generic Enabler (reference) instance.
==================  =============

Last but not least, the repository is structured in branchs:

- master, stable version, at the end of a Release n, we make a pull request from Release n-1 in develop to master
- develop, default work branch.
- feature/<GEri/GEi-name>, branch used to the GEri/GEi owner to upload the content. When you consider that the scripts
are correct you should launch a pull request to develop. FIWARE Lab team will check the scripts in order to secure that
it is working and if all is correct we will accept the pull request to develop branch.