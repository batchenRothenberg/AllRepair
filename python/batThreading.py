# Thread which passes exceptions to its caller
# Based on answer from: https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python/12223550#12223550
import sys
import threading


class ExcThread(threading.Thread):

  def run(self):
    self.exc = None
    try:
      # Possibly throws an exception
      threading.Thread.run(self)
    except:
      self.exc = sys.exc_info()
      # Save details of the exception thrown but don't rethrow,
      # just complete the function

  def join(self, timeout):
    threading.Thread.join(self, timeout)
    if self.exc:
        sys.exit(self.exc[1])