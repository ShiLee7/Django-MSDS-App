FROM nginx:1.25

# Remove the default site config
RUN rm /etc/nginx/conf.d/default.conf

# ✅ Fix: Copy `nginx.conf` to `/etc/nginx/`
COPY nginx.conf /etc/nginx/nginx.conf

# ✅ If you want site-specific config, rename it as `default.conf`
#COPY default.conf /etc/nginx/conf.d/default.conf