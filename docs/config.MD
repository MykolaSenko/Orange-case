# Configuration

The `Scraper` reads a configuration file in json format in order to know how to navigate pages and which pages to scrape. The file has to be inside the `config` folder and it's name follows this pattern: `<provider>_config.json`, for example the current repository contains `telenet_promo_config.json`, `telenet_packs_config.json`, `mobile-vikings_config.json` among others. Each one of those files provides specific information on how to navigate those providers/subsections (as you can see telenet is split into 2 files for easier use). When instatiating the class Scraper, you need to provide a string telling which configuration file to use (you should ignore the suffix `_config.json`, for example `my_telenet_scraper = Scraper('telenet_promo')`).

The config file itself follows this format:

![Diagram](../assets/basic_diagram.png)

The `start` key contains a dictionary with 3 elements:

- `url` (mandatory): Specifies the starting url for the scraper
- `locator` (mandatory): Specifies which part of the page to look for links
- `iterator_size` (optional): In case the above locator returns more objects than desired, this parameter can speficy a maximum number of values to be considered. It's best practice to use a more precise `locator`, but that's not always possible.

![Start key](../assets/start.png)

The `param` key is composed of a dict whose keys are spefic page identifiers. An indentifier is any part of an url to which this configuration should apply. One of the keys of this dictionary has to be `default` so that it's configuration can be used both as the starting building block for other configurations but also to be used completely when no specific configuration is avaliable.

![Params](../assets/params.png)

In this case our `params` dict contains the `default` key (as it is mandatory) but also a `subscription` key (the url identifier). In this case any URL containing the word `subscription` will have the configuration defined applied to it. You can create as many URL identifiers as you need. 

Each url identifier always contains 2 dictionaries: `navigation` and `data`. Let's look into `navigation` first:

- `iterator` (mandatory): Specifies which part of the page to iterate through looking for information.
- `iterator_size` (mandatory): In case the above locator returns more objects than desired, this parameter can speficy a maximum number of values to be considered. It's best practice to use a more precise `iterator`, but that's not always possible.
- `sub_link_tag` (mandatory): Specifies the links to look for inside the return of `iterator`. If no link is found, the scraper assumes that this is the page that should be scraped and stops navigating to start scraping.
- `page_load` (mandatory): Before doing anything on the page wait for the specified css element to show up.
- `url_prefix` (optional): In case the links require a prefix.

![Navigation key](../assets/navigation.png)

The `data` dictionary contains information on how to scrape the given page. It contains information about the fields to be scraped and how to find the element that contain them. The key name is the name of the field to be scraped (as it will show in the final csv file) and it's contents must involve:

- `tag` (mandatory): How to find that element.
- `multiple` (optional): In case the tag above returns more than one element and all of them must be concatenated as part of the result. Deafult is `false`
- `re` (optional): In case a regex pattern is to be applied to the field. The value includes the pattern and depending on the value of `re_type`, also what should substitute the match.
- `re_type` (optional): In case there's is a regex to be applied, what kind. Acceptable values are `sub` and `search`.

![Data](../assets/data.png)

In this example we are scraping 3 different fields that we called:
- `name` Can be found using the specified tag.
- `description` The specified tag results multiple elements and we want all of them.
- `initial_price` The tag returns a value that is cleaned using a regex. Since the type is `sub`, the `re` key is a list whose second element is what should be used instead of what is matched. In this case €, spaces, line breaks and dashes will be substituted by empty space.

It's important to note that configurations for all pages will be built _on top_ of the default configuration, which means that the fields specified will be added/replace the fields present in the default. This is done so that one does not need to rewrite the entire configuration for each page, you just need to replace what's special or add what is specific, while the default configuration contains what is common (or expected) to all pages.

The examples shown above were taken from the file `sample_config.json` which can be found on the `config` folder. Other pre setup configuration are also present in that folder and should be used as a reference.