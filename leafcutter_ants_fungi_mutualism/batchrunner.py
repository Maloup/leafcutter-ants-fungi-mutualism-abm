from tqdm import tqdm
from multiprocess import Pool, cpu_count

from mesa.batchrunner import BatchRunner


class BatchRunnerMP(BatchRunner):
    """Child class of BatchRunner, extended with multiprocessing support."""

    def __init__(self, model_cls, nr_processes=None, **kwargs):
        """Create a new BatchRunnerMP for a given model with the given
        parameters.

        model_cls: The class of model to batch-run.
        nr_processes: int
                      the number of separate processes the BatchRunner
                      should start, all running in parallel.
        kwargs: the kwargs required for the parent BatchRunner class
        """
        if nr_processes is None:
            # identify the number of processors available on users machine
            available_processors = cpu_count()
            self.processes = available_processors
            print(f"BatchRunner MP will use {self.processes} processors.")
        else:
            self.processes = nr_processes

        super().__init__(model_cls, **kwargs)
        self.pool = Pool(self.processes)

    def _make_model_args_mp(self):
        """Prepare all combinations of parameter values for `run_all`
        Due to multiprocessing requirements of @StaticMethod takes different input, hence the similar function
        Returns:
            List of list with the form:
            [[model_object, dictionary_of_kwargs, max_steps, iterations]]
        """
        total_iterations = self.iterations
        all_kwargs = []

        count = len(self.parameters_list)
        if count:
            for params in self.parameters_list:
                kwargs = params.copy()
                kwargs.update(self.fixed_parameters)
                # run each iterations specific number of times
                for iter in range(self.iterations):
                    kwargs_repeated = kwargs.copy()
                    all_kwargs.append(
                        [self.model_cls, kwargs_repeated, self.max_steps, iter]
                    )

        elif len(self.fixed_parameters):
            count = 1
            kwargs = self.fixed_parameters.copy()
            all_kwargs.append(kwargs)

        total_iterations *= count

        return all_kwargs, total_iterations

    @staticmethod
    def _run_wrappermp(iter_args):
        """
        Based on requirement of Python multiprocessing requires @staticmethod decorator;
        this is primarily to ensure functionality on Windows OS and does not impact MAC or Linux distros

        :param iter_args: List of arguments for model run
            iter_args[0] = model object
            iter_args[1] = key word arguments needed for model object
            iter_args[2] = maximum number of steps for model
            iter_args[3] = number of time to run model for stochastic/random variation with same parameters
        :return:
            tuple of param values which serves as a unique key for model results
            model object
        """

        model_i = iter_args[0]
        kwargs = iter_args[1]
        max_steps = iter_args[2]
        iteration = iter_args[3]

        # instantiate version of model with correct parameters
        model = model_i(**kwargs)
        while model.running and model.schedule.steps < max_steps:
            model.step()

        # add iteration number to dictionary to make unique_key
        kwargs["iteration"] = iteration

        # convert kwargs dict to tuple to  make consistent
        param_values = tuple(kwargs.values())

        return param_values, model

    def _result_prep_mp(self, results):
        """
        Helper Function
        :param results: Takes results dictionary from Processpool and single processor debug run and fixes format to
        make compatible with BatchRunner Output
        :updates model_vars and agents_vars so consistent across all batchrunner
        """
        # Take results and convert to dictionary so dataframe can be called
        for model_key, model in results.items():
            if self.model_reporters:
                self.model_vars[model_key] = self.collect_model_vars(model)
            if self.agent_reporters:
                agent_vars = self.collect_agent_vars(model)
                for agent_id, reports in agent_vars.items():
                    agent_key = model_key + (agent_id,)
                    self.agent_vars[agent_key] = reports
            if hasattr(model, "datacollector"):
                if model.datacollector.model_reporters is not None:
                    self.datacollector_model_reporters[
                        model_key
                    ] = model.datacollector.get_model_vars_dataframe()
                if model.datacollector.agent_reporters is not None:
                    self.datacollector_agent_reporters[
                        model_key
                    ] = model.datacollector.get_agent_vars_dataframe()

        # Make results consistent
        if len(self.datacollector_model_reporters.keys()) == 0:
            self.datacollector_model_reporters = None
        if len(self.datacollector_agent_reporters.keys()) == 0:
            self.datacollector_agent_reporters = None

    def run_all(self):
        """
        Run the model at all parameter combinations and store results,
        overrides run_all from BatchRunner.
        """

        run_iter_args, total_iterations = self._make_model_args_mp()
        # register the process pool and init a queue
        # store results in ordered dictionary
        results = {}

        if self.processes > 1:
            with tqdm(total_iterations, disable=not self.display_progress) as pbar:
                for params, model in self.pool.imap_unordered(
                    self._run_wrappermp, run_iter_args
                ):
                    results[params] = model
                    pbar.update()

                self._result_prep_mp(results)
        # For debugging model due to difficulty of getting errors during multiprocessing
        else:
            for run in run_iter_args:
                params, model_data = self._run_wrappermp(run)
                results[params] = model_data

            self._result_prep_mp(results)

        # Close multi-processing
        self.pool.close()

        return (
            getattr(self, "model_vars", None),
            getattr(self, "agent_vars", None),
            getattr(self, "datacollector_model_reporters", None),
            getattr(self, "datacollector_agent_reporters", None),
        )
