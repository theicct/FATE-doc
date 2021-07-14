---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
title: FATE Documentation
---

The [ICCT](https://theicct.org/)'s Fast Assessment of Transportation Emissions (FATE) model evaluates air quality and health impacts associated with present or future changes in air pollutant emissions from 9 sectors, including 3 transportation sub-sectors. The tool estimates the national population-weighted ambient PM2.5 exposure (annual average in µg/m3) for 181 countries and ozone (O3) exposure (6-month average of the 1hr or 8h daily maximum O3 in ppb) for 19 individual G20 countries and 24 additional EU member countries. It also outputs the number of premature deaths and disability-adjusted life years (DALYs) associated with exposure to these two pollutants. Supplementary outputs of the tool include baseline exposures to ambient PM2.5 and O3 and detailed health impacts by ambient pollutant, disease, and age group. Health outputs of the tool also include 5th and 95th percentile estimates that reflect uncertainty in the concentration-response relationship.

FATE is a reduced-complexity air quality model, allowing users to simulate multiple global scenarios without the high computational costs usually required by chemical transport models. The extent to which exposures of PM2.5 and O3 are sensitive to changes in pollutant emissions, denoted as sensitivities, are calculated using the adjoint of the GEOS-Chem model. The health impacts associated with exposure to these pollutants are calculated using methods consistent with the GBD 2019. The tool is designed to accommodate future updates to GBD health impact assessment methods. To estimate health impacts in future years, the tool considers projected changes in population, age distributions, and baseline disease rates.


## Versions

FATE is under continuing development. Documentation of all versions since v0.3 can be found here.

{% assign pages = site.pages | sort: "title" | reverse %}
{% for page in pages %}
{% if page.dir contains '/versions/' and page.title contains 'FATE v'%}
<li><a class="page-link" href="{{ page.url | relative_url }}">{{ page.title | escape }}</a></li>
{% endif %}
{% endfor %}
