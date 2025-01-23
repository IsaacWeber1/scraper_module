import json
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('output.json', 'w', encoding='utf8')
        self.file.write('[\n')  # Start the JSON array
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]\n')  # End the JSON array
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')  # Add a comma between JSON objects
        else:
            self.first_item = False
        line = json.dumps(dict(item), ensure_ascii=False, indent=4)
        self.file.write(line)
        return item
    
class ScraperModulePipeline:
    def process_item(self, item, spider):
        return item