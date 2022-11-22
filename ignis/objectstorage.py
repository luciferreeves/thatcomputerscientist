from .models import Object, ObjectDirectory

class ObjectStorage:
    def create_directory(self, name):
        if not ObjectDirectory.objects.filter(name=name).exists():
            ObjectDirectory.objects.create(name=name)

    def rename_directory(self, old_name, new_name):
        if not ObjectDirectory.objects.filter(name=old_name).exists():
            ObjectDirectory.objects.create(name=old_name)
        ObjectDirectory.objects.filter(name=old_name).update(name=new_name)

    def delete_directory(self, name):
        Object.objects.filter(location=ObjectDirectory.objects.get(name=name)).delete()
        ObjectDirectory.objects.filter(name=name).delete()

    def create_object(self, md5, metadata, data, name):
        if not ObjectDirectory.objects.filter(name=name).exists():
            ObjectDirectory.objects.create(name=name)
        if not Object.objects.filter(md5=md5).exists():
            Object.objects.create(md5=md5, metadata=metadata, data=data, location=ObjectDirectory.objects.get(name=name))

    def delete_object(self, slug, md5):
        Object.objects.filter(location=ObjectDirectory.objects.get(name=slug), md5=md5).delete()

    def get_object(self, slug, md5):
        return Object.objects.get(location=ObjectDirectory.objects.get(name=slug), md5=md5)

    def object_exists(self, slug, md5):
        return Object.objects.filter(location=ObjectDirectory.objects.get(name=slug), md5=md5).exists()

    def get_directory_contents(self, name):
        return Object.objects.filter(location=ObjectDirectory.objects.get(name=name))

    def get_directories(self):
        return ObjectDirectory.objects.all()
