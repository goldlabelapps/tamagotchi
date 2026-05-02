# Jinja2 Templates

The Tamagotchi app is primarily a REST API, but it also serves HTML pages when a browser visits certain URLs. Those pages are built with **Jinja2**, the template engine that ships with Flask.

---

## 1. What is a Template Engine?

Instead of building HTML strings by hand in Python (messy and insecure), you write an HTML file with special placeholders. The template engine fills in the placeholders with real data at request time and returns the finished HTML.

```
Template (pets_list.html) + Pet data  →  Jinja2  →  Final HTML sent to browser
```

---

## 2. Template Location

Flask looks for templates in the `templates/` directory relative to the application. In this project that is `src/templates/`:

```
src/templates/
  base.html       ← shared layout
  home.html       ← home page
  pets_list.html  ← list of all pets
  pet_detail.html ← single pet details
```

When you call `render_template("pets_list.html", pets=pet_dicts)` in a route, Flask:
1. Finds `src/templates/pets_list.html`
2. Passes the `pets` variable into it
3. Renders the template and returns HTML

---

## 3. Template Inheritance

Repeating the header, navigation, and footer in every page would be tedious. Jinja2 solves this with **template inheritance**.

### `base.html` — the parent template

`base.html` defines the full page skeleton and marks areas that child templates can fill in:

```html
<TITLE>{% block title %}Tamagotchi APP°{% endblock %}</TITLE>
...
{% block content %}{% endblock %}
```

`{% block name %}...{% endblock %}` defines a named slot. The default content (between the tags) is used if a child does not override it.

### `home.html` — a child template

```html
{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
  <h1>Welcome!</h1>
  ...
{% endblock %}
```

`{% extends "base.html" %}` tells Jinja2 to use `base.html` as the layout. Each `{% block %}` then fills in the corresponding slot. Anything outside a block tag in a child template is ignored.

---

## 4. Variables

Pass data from Python to the template using keyword arguments to `render_template()`:

```python
# In the route
return render_template("pets_list.html", pets=pet_dicts), 200
```

In the template, use `{{ variable }}` to output a value:

```html
{% for pet in pets %}
  <td>{{ pet.name }}</td>
  <td>{{ pet.health }}%</td>
{% endfor %}
```

`{{ pet.name }}` calls `str()` on the value and inserts it into the HTML. Jinja2 also **auto-escapes** variables by default, so values like `<script>` are rendered as `&lt;script&gt;` rather than executable HTML. This prevents **Cross-Site Scripting (XSS)** attacks.

---

## 5. Control Structures

### `{% if %}`

```html
{% if pet.is_alive %}
  <font color="#008000"><b>Alive</b></font>
{% else %}
  <font color="#FF0000"><b>Deceased</b></font>
{% endif %}
```

### `{% for %}`

```html
{% for pet in pets %}
  <tr>
    <td>{{ pet.name }}</td>
  </tr>
{% endfor %}
```

Jinja2's `for` loops provide a special `loop` object inside the loop body:

| Variable | Value |
|----------|-------|
| `loop.index` | Current iteration (1-based) |
| `loop.index0` | Current iteration (0-based) |
| `loop.first` | `True` on the first iteration |
| `loop.last` | `True` on the last iteration |

Used in `pets_list.html` to alternate row background colours:

```html
<tr bgcolor="{% if loop.index is odd %}#FFFFFF{% else %}#F0F0F0{% endif %}">
```

### `{% if %}` with `else` (empty state)

```html
{% if pets %}
  ... table of pets ...
{% else %}
  <p>You have no pets yet!</p>
{% endif %}
```

---

## 6. Filters

Filters transform a variable's value using the `|` operator:

```html
{{ pet.health|int }}         ← converts float to int
{{ pet.created_at[:10] }}    ← Python slice — first 10 characters of the string
```

In `pet_detail.html`, filters are used to build CSS progress bars:

```html
<td width="{{ [pet.health|int, 1]|max }}%"  ...>
```

`[pet.health|int, 1]|max` is a Jinja2 expression that creates a Python list `[health_as_int, 1]` and takes the maximum value, ensuring the progress bar is always at least 1% wide.

---

## 7. Content Negotiation — JSON or HTML?

The `list_pets` and `get_pet` routes in `src/routes/pets.py` serve either JSON or HTML depending on the `Accept` header:

```python
best = request.accept_mimetypes.best_match(["application/json", "text/html"])
if best == "text/html":
    return render_template("pets_list.html", pets=pet_dicts), 200
return jsonify({"pets": pet_dicts}), 200
```

When you visit `http://localhost:5555/api/pets` in a browser, the browser's `Accept: text/html` header triggers the HTML path. A `curl` call or the test suite sends `Accept: application/json` and gets JSON.

---

## 8. The Retro Aesthetic

The templates use old-school HTML 3.2 table-based layout with `<FONT>` and `<TABLE>` tags — a deliberate stylistic choice to evoke the 1990s era of the original Tamagotchi toy. Modern websites use CSS Grid and Flexbox instead, but the Jinja2 template concepts are identical regardless of the HTML style.

---

## Further Reading

- [Jinja2 documentation](https://jinja.palletsprojects.com/)
- [Flask template guide](https://flask.palletsprojects.com/en/latest/templating/)
