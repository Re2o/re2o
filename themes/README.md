# Custom themes for Re2o

The following themes are licensed under MIT to Thomas Park. See https://bootswatch.com.

By default, only the default.css is enabled, which is a blank css file.

**How to activate new themes ?**

You can activate themes by copying them, or making a symbolic link to the `static/css/themes` directory and collecting the statics.

**How to change the default theme ?**

You can change the default theme by changing the default.css file.

**How to add new theme ?**

You can add a brand new theme by adding a css file to the `static/css/themes` directory and collecting the statics.

**What happens if I delete a theme ?**

User with this theme will continue to try to load this theme, without success if the theme was correctly deleted. It won't cause any malfunctions on the client side, and the default re2o theme (but not the default.css) theme will be loaded. Users will not be able to select this theme anymore afterwards.

Try to not delete the default.css theme.