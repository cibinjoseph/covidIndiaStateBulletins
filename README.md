# covidIndiaStateBulletins
Python3 module to get latest COVID bulletins from Indian state health department webpages

## Usage:
**Example 1**: To download the latest COVID bulletin for Delhi, use
 the function `getDelhi()`.
```python
import covidIndiaStateBulletins as co

# Initialize module 
co.init()

# Get bulletin from Delhi Health Department website
bulletinDate, bulletinLink, lastUpdatedDate = co.getDelhi()

print(bulletinDate)     # Bulletin date
print(bulletinLink)     # Link to latest bulletin
print(lastUpdatedDate)  # Last updated date 
```

# Documentation
All pdf bulletins are downloaded to `resources/` directory in current path.  

### Available state bulletins
* Andhra Pradesh
* Delhi
* Kerala
* Telangana

### Available functions
For a list of all available functions, import the module and use help():   
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
