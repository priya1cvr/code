 
from mrjob.job import MRJob 
from mrjob.step import MRStep

class MostPopularSuperHero(MRJob):

    def configure_options(self):
        super(MostPopularSuperHero, self).configure_options()
        self.add_file_option('--names', help='Path to marvel-names.txt')

    def steps(self):
        return[
            MRStep(mapper=self.mapper_get_friends,
                   reducer=self.reducer_combine_friends),
            MRStep(mapper_init=self.load_name_dictionary,
                   mapper=self.mapper_prep_for_sort,
                   reducer=self.reducer_find_max_friends)
        ]
    # mapper extracts the key and value we care about ,here key is userID and value is its occurence 
    def mapper_get_friends(self,_,line):
        heroID=line.split()[0]
        friendsList=line.split()[1:]
        yield int(heroID),int(len(friendsList))

    def reducer_combine_friends(self,heroID,totalFriends):
        yield heroID,sum(totalFriends)

    def load_name_dictionary(self):
        self.heroNames= {}
        with open("marvel-names.txt") as f:
            for line in f:
                fields=line.split(' "')
                heroID = int(fields[0])
                self.heroNames[heroID] = fields[1].decode('utf-8', 'ignore')


    def mapper_prep_for_sort(self,heroID,totalFriends):
        heroName=self.heroNames[heroID]
        yield None,(totalFriends,heroName)

    # to this reducer every key has value none and values are like [(300,241) ,(124,782),(534,50)] .... where 1st part is # of occurence of the movie and 2nd part is movieID
    def reducer_find_max_friends(self,key,values):
        yield max(values)


if __name__=='__main__':
    MostPopularSuperHero.run()  


''' command to execute is :
python 9_MostPopularSuperHero.py --names=marvel-names.txt marvel-graph.txt
'''       
