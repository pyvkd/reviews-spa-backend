# testimonial-spa-backend
Small App to manage testimonials for a SPA

How to use:

1. Create a env or anyway you manage your python installation and run the following command to install required libraries

`shell
pip install -r requirements.txt
`
2. Setup the sqlite db:

`shell
python createdb.py
`
3. Run the app with gunicorn

`shell
gunicorn app:app
`

4. Expose with nginx or other server to be used as api.

site-nginx.conf : 

`conf
 server {
 ..
 location /api/v1/review {
    proxy_pass http://localhost:8080/;
 }
 ..
 }
`
