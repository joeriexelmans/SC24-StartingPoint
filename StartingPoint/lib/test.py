import abc
from difflib import ndiff

from lib.controller import Controller, pretty_time
from lib.tracer import Tracer
from lib.yakindu_helpers import YakinduTimerServiceAdapter, trace_output_events

class AbstractEnvironmentState:
    # should return the new state after handling the event
    @abc.abstractmethod
    def handle_event(self, event_name, param):
        pass
    # should compare states *by value*
    @abc.abstractmethod
    def __eq__(self, other):
        pass

# # Can we ignore event in 'trace' at position 'idx' with respect to idempotency?
# def can_ignore(trace, idx):
#     (timestamp, event_name, value) = trace[idx]
#     if event_name in IDEMPOTENT:
#         # If the same event occurred earlier, with the same parameter value, then this event can be ignored:
#         for (earlier_timestamp, earlier_event_name, earlier_value) in reversed(trace[0:idx]):
#             if (earlier_event_name, earlier_value) == (event_name, value):
#                 # same event name and same parameter value (timestamps allowed to differ)
#                 return True
#             elif event_name == earlier_event_name:
#                 # same event name, but different parameter value:
#                 # stop looking into the past:
#                 break
#         # If the same event occurs later event, but with the same timestamp, this event is overwritten and can be ignored:
#         for (later_timestamp, later_event_name, later_value) in trace[idx+1:]:
#             if (later_timestamp, later_event_name) == (timestamp, event_name):
#                 # if a later event with same name and timestamp occurs, ours will be overwritten:
#                 return True
#             if later_timestamp != timestamp:
#                 # no need to look further into the future:
#                 break
#     return False

def postprocess_trace(trace, environment_class):
    env_state = environment_class()
    filtered_trace = []
    # Remove events that have no effect:
    for timestamp, event_name, param in trace:
        new_env_state = env_state.handle_event(event_name, param)
        if new_env_state != env_state:
            # event had an effect
            filtered_trace.append((timestamp, event_name, param))
        env_state = new_env_state
    return filtered_trace

def compare_traces(expected, actual):
    i = 0
    while i < len(expected) and i < len(actual):
        # Compare tuples:
        if expected[i] != actual[i]:
            print("Traces differ!")
            # print("expected: (%i, \"%s\", %s)" % expected[i])
            # print("actual: (%i, \"%s\", %s)" % actual[i])
            return False
        i += 1
    if len(expected) != len(actual):
        print("Traces have different length:")
        print("expected length: %i" % len(expected))
        print("actual length: %i" % len(actual))
        return False
    print("Traces match.")
    return True

def run_scenario(input_trace, expected_output_trace, statechart_class, environment_class, verbose=False):
    controller = Controller()
    sc = statechart_class()
    tracer = Tracer(verbose=False)
    controller.input_tracers.append((sc, tracer.record_input_event))
    trace_output_events(controller, sc, callback=tracer.record_output_event)
    sc.timer_service = YakinduTimerServiceAdapter(controller)

    # Put entire input trace in event queue, ready to go!
    for tup in input_trace:
        (timestamp, event_name, value) = tup
        controller.add_input(sc, event_name, timestamp, value)

    sc.enter() # enter default state(s)
    
    if len(expected_output_trace) > 0:
        last_output_event_timestamp = expected_output_trace[-1][0]
    else:
        last_output_event_timestamp = 0

    # Blocking synchronous call:
    controller.run_until(last_output_event_timestamp)

    actual_output_trace = tracer.output_events

    clean_expected = postprocess_trace(expected_output_trace, environment_class)
    clean_actual   = postprocess_trace(actual_output_trace, environment_class)

    def print_diff():
        # The diff printed will be a diff of the 'raw' traces, not of the cleaned up traces
        # A diff of the cleaned up traces would be confusing to the user.
        have_plus = False
        have_minus = False
        have_useless = False
        for diffline in ndiff(
                [str(tup)+'\n' for tup in expected_output_trace],
                [str(tup)+'\n' for tup in actual_output_trace],
                charjunk=None,
            ):
            symbol = diffline[0]
            if symbol == '+':
                have_plus = True
            if symbol == '-':
                have_minus = True
            if symbol == '?':
                continue
            rest = diffline[2:-1] # drop last character (=newline)
            useless_line = (
                   symbol == '-' and rest not in [str(tup) for tup in clean_expected]
                or symbol == '+' and rest not in [str(tup) for tup in clean_actual]
                # or symbol == ' ' and rest not in [str(tup) for tup in clean_actual]
            )
            if useless_line:
                print(" (%s) %s" % (symbol, rest))
                have_useless = True
            else:
                print("  %s  %s" % (symbol, rest))

        if have_minus or have_plus or have_useless:
            print("Legend:")
        if have_minus:
            print("  -: expected, but did not happen")
        if have_plus:
            print("  +: happened, but was not expected")
        if have_useless:
            print("  (-) or (+): indicates a \"useless event\" (because it has no effect), either in expected output (-) or in actual output (+).")
            print("\n\"Useless events\" are ignored by the comparison algorithm, and will never cause your test to fail. In this assignment, your solution is allowed to contain useless events.")

    if not compare_traces(clean_expected, clean_actual):
        # even though we compared the 'normalized' traces, we print the *raw* traces, not to confuse the user!
        print("Raw diff between expected and actual output event trace:")
        print_diff()
        return False
    elif verbose:
        print_diff()
    return True

def run_scenarios(scenarios, statechart_class, environment_class, verbose=True):
    ok = True
    for scenario in scenarios:
        print(f"Running scenario: {scenario["name"]}")
        ok = run_scenario(scenario["input_events"], scenario["output_events"], statechart_class, environment_class, verbose=verbose) and ok
        print("--------")
    if ok:
        print("All scenarios passed.")
    else:
        print("Some scenarios failed.")
