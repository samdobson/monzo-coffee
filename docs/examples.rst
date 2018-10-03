:github_url: https://github.com/samdobson/monzo-coffee/edit/master/docs/examples.rst


Available fields
================

.. literalinclude:: txn.txt
   :language: python
   :emphasize-lines: 4,11,38,60,70
   :linenos:


Examples
--------

#coffee: `txn['merchant']['name'] in ('Starbucks', 'Costa Coffee')`

#usa2018: `txn['merchant']['address']['country'] = 'USA' and txn['merchant']['online'] == False`

