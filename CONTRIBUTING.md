Thanks for your interest in Halliwell! I really appreciate your taking the time
to make it better. The basics for code contribution are as follows:

 - Adhere to the [Python style guide]. Pylint checking will be enabled once
   [this issue] has been closed, but in the meantime you can look at the
   existing code to see how things are laid out.
 - Any new functionality should be reasonably well covered with automated
   testing (I aim for 100% coverage, but this isn't a requirement for
   contribution - do cover the *"happy path"*, though).
    - The IMDb interaction has additional integration tests; if you add to
      these, please annotate them with `@slow` to allow them to be excluded
      during development.
 - Please [write a good commit message] when contributing.

## Issues

This project uses GitHub's issue tracker, feel free to open a new issue if you
find a problem in the current version. The more detail the better, though, and
do take the time to search for existing, similar issues.

Issues that are off the primary development track but would still be useful
functionality are tagged [Help Wanted]. These are a good place to start if you
haven't found a specific problem, but would like to help out. Please add a
comment if you start working on one of these, to avoid duplication of effort
(similarly, if you later stop working on it, do let everyone know).

## Behaviour

This project adheres to the [Contributor Covenant]; if you see any behaviour
that violates this code of conduct, report it to <mail@jonrshar.pe>.

  [contributor covenant]: http://contributor-covenant.org/version/1/3/0/
  [help wanted]: https://github.com/textbook/halliwell/labels/help%20wanted
  [python style guide]: https://www.python.org/dev/peps/pep-0008/
  [this issue]: https://github.com/PyCQA/pylint/issues/654
  [write a good commit message]: https://github.com/erlang/otp/wiki/Writing-good-commit-messages