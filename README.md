# covidIndiaStateBulletins
Python module to get latest COVID bulletins from Indian state health department webpages

## Usage:
**Example 1**: Download latest pdf COVID bulletin for Delhi
```python
import covidIndiaStateBulletins as co

co.init()
bulletinDate, bulletinLink, lastUpdatedDate = co.getDelhi()

print(bulletinDate.strftime('%d.%m.%Y'))     # Bulletin date in specified format
print(bulletinLink)                          # Link to latest bulletin
print(lastUpdatedDate.strftime('%d.%m.%Y'))  # Last updated date in specified format
```

# Documentation
### Available functions
For a list of available functions, import the module and use help():   
```python
import covidIndiaStateBulletins as co
help(co)
```
### For use as an API
All `getState()` functions return a list of arguments in the form:
```python
[bulletinDate, bulletinLink, lastUpdatedDate]
```
All dates are of the `datetime` class in python3 and links are of `string` type.

## Contributing
All contributions through pull requests only.
