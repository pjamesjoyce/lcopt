---
title: 'Lcopt - An interactive tool for creating fully parameterised Life Cycle Assessment (LCA) foreground models'
tags:
  - example
  - tags
  - for the paper
authors:
 - name: P James Joyce
   orcid: 0000-0002-9560-3132
   affiliation: 1
affiliations:
 - name: KTH Royal Institute of Technology
   index: 1
date: 24 July 2017
bibliography: paper.bib
---

# Summary

Lcopt is an open source Python package for creating fully parameterised Life Cycle Assessment (LCA) foreground models. Lcopt includes an intuitive Flask [@Ronacher2017] based user interface to greatly simplify the modelling process for LCA practitioners and researchers. Background Life Cycle Inventory (LCI) data from the ecoinvent 3.3 database [@EcoinventCentre2016], or the FORWAST I/O database [@Forwast2007] can be linked to the foreground models. Models are created by drawing flow sheets. Each link in the flow sheet is assigned a parameter which can either be set directly or calculted using user defined functions. Any number of parameter sets representing variations of the model can be created in order to undertake scenario analysis and options appraisal. Once created, the models can be analysed directly from within the Flask interface, utilising Brightway [@Mutel2017] to generate the LCA results. This includes hotspot identification, process contribution and scenario comparison. If required, the models can also be exported to commonly used LCA softwares (Brightway [@Mutel2017] and SimaPro [@PreSustainability2014]) for further, more comprehensive analysis. The source code repository is hosted on github [@Joyce2017Repository] and full online documentation is available [@Joyce2017].

# References