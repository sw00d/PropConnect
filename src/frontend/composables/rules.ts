export const useFormRules = () => {
	return {
		ruleRequired: (v: any) => !!v || "Required",
		ruleEmail: (value: any) => {
			const pattern =
				/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
			return pattern.test(value) || "Enter a valid email";
		},
		ruleIntroMessage: (v: string) => (!!v && v.length < 800) || "Cannot be more than 800 characters",
	};
};
