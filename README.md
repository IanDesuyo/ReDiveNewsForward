# Re:Dive News Forward

A simple webcrawler to catch プリコネR official news then send to Discord via webhook

## Getting Started

Create a sqlite database with below table and saved at ``app.db``

#### NewsChannel
| id(BigInt) | token(Str) | tw(Bool) | jp(Bool) | custom(Bool) |
|-|-|-|-|-|
| Webhook URL | Webhook Token | TW server | JP server | Use default avatar or not |
| 741265589254881323 | nW0sAqhjJkhosNWF5lRWCjBn5Xssku6QNhAK068tjsyVXx8r7EriGlmb_8X8XsBYyEvw | 1 | 1 | 0 |

Then use crontab to run ``news_jp.py`` and ``news_tw.py`` at anytime you want, like

``` py
*/5 * * * * python3 /path/to/news_jp.py
*/5 * * * * python3 /path/to/news_tw.py
```
