from bot import LOGGER
from markdownify import markdownify

# utilities used by rsshandler
class UtilHandler():
    # validates templates and formats a given feed
    def format_items(self, rss_d, item_no, template):

        """
        this function returns a tuple containing a bool value and
        a formatted feed item of type string, based on the template
        """

        self.keys = [
            'feed_name', 'feed_link', 'item_name',
            'item_link', 'item_description', 'item_enclosures',
            'white_space', 'tab_space', 'new_line'
        ]

        # template string is validated by comparing values of two lists
        template = template.split('|')
        if any(x not in self.keys for x in template):
            return ("Incorrect Syntax. Hit /template to get it's usage.",)
        try:
            self.values = [
                f'<b>{rss_d.feed.title}</b>',
                f'{rss_d.feed.link}',
                f'<b>{rss_d.entries[item_no]["title"]}</b>',
                f'{rss_d.entries[item_no]["link"]}',
                markdownify(f'{rss_d.entries[item_no]["description"] or "NULL"}', strip=['img']),
                f'{rss_d.entries[item_no].enclosures[0].href if rss_d.entries[0].enclosures else "NULL"}',
                ' ',
                '\t',
                '\n',
            ]

            # combine two lists to represent a key-value pair (dict)
            rss_d = dict(zip(self.keys, self.values))
            return (True, "".join([rss_d[key] for key in template]))
        except AttributeError:
            LOGGER.error('There was an error while parsing this feed due to an unknown server error.')

utilities = UtilHandler()
