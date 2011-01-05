""" Selects an object from the project on Pivotal Tracker to start
    working on.
"""

import logging
from base import Base

def format_filter(qs):
    filters = ['%s:%s' for k,v in qs.items()]
    return ' '.join(filters)

class Pick(Base):

    @property
    def type(self):
        raise NotImplementedError('Must define in subclass')

    @property
    def plural_type(self):
        raise NotImplementedError('Must define in subclass')

    @property
    def branch_suffix(self):
        raise NotImplementedError('Must define in subclass')

    _story = None
    @property
    def story(self):
        if not self._story:
            qs = {'state': 'unstarted',
                  'type': self.type,
                  }
            if self.options.get('only_mine'):
                qs['owned_by'] = self.options['full_name']
            
            stories = self.project.stories(filter=format_filter(qs))
            if len(stories):
                self._story = stories[0]
            
        return self._story
        
    
    def __call__(self):
        super(Pick, self).__call__()
        
        msg = 'Retrieving latest %s from Pivotal Tracker' % self.plural_type
        if self.options['only_mine']:
            msg += " for" + self.options['full_name']

        self.put(msg)
      
        if self.story is None:
            self.put('No %s available!' % self.plural_type)
            return
    
        self.put('Story: #{story.name}')
        self.put('URL: #{story.url}')

        self.put('Updating #{type} status in Pivotal Tracker...')
        #if story.start!(:owned_by => options[:full_name])
    
      #   suffix = branch_suffix
      #   unless options[:quiet]
      #     put "Enter branch name (will be prepended by #{story.id}) [#{suffix}]: ", false
      #     suffix = input.gets.chomp
      
      #     suffix = "feature" if suffix == ""
      #   end

      #   branch = "#{story.id}-#{suffix}"
      #   if get("git branch").match(branch).nil?
      #     put "Creating #{branch} branch..."
      #     sys "git checkout -b #{branch}"
      #   end
    
      #   return 0
      # else
      #   put "Unable to mark #{type} as started"
        
      #   return 1

'''
class Pick < Base
  
    def type
      raise Error("must define in subclass")
    end
    
    def plural_type
      raise Error("must define in subclass")
    end
  
    def branch_suffix
      raise Error("must define in subclass")
    end
    
    def run!
      super

      msg = "Retrieving latest #{plural_type} from Pivotal Tracker"
      if options[:only_mine]
        msg += " for #{options[:full_name]}"
      end
      put "#{msg}..."
      
      unless story
        put "No #{plural_type} available!"
        return 0
      end
    
      put "Story: #{story.name}"
      put "URL: #{story.url}"

      put "Updating #{type} status in Pivotal Tracker..."
      if story.start!(:owned_by => options[:full_name])
    
        suffix = branch_suffix
        unless options[:quiet]
          put "Enter branch name (will be prepended by #{story.id}) [#{suffix}]: ", false
          suffix = input.gets.chomp
      
          suffix = "feature" if suffix == ""
        end

        branch = "#{story.id}-#{suffix}"
        if get("git branch").match(branch).nil?
          put "Creating #{branch} branch..."
          sys "git checkout -b #{branch}"
        end
    
        return 0
      else
        put "Unable to mark #{type} as started"
        
        return 1
      end
    end

  protected

    def story
      return @story if @story
      
      conditions = { :story_type => type, :current_state => :unstarted }
      conditions[:owned_by] = options[:full_name] if options[:only_mine]
      @story = project.stories.find(:conditions => conditions, :limit => 1).first
'''
