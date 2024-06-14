from io import StringIO, BytesIO
from matplotlib.figure import Figure
from viktor.views import SummaryItem, Summary
from viktor.views import (
    ImageResult
)

from pathlib import Path
import pandas as pd
from anastruct import SystemElements, LoadCase, LoadCombination

from munch import Munch
from viktor import ViktorController, UserError

from viktor.core import Storage
from viktor.parametrization import (
    ViktorParametrization,
    OptionField,
    Tab,
    AutocompleteField,
    LineBreak,
    OptimizationButton, NumberField, HiddenField, OutputField, TextField
)
from viktor.result import OptimizationResultElement, OptimizationResult
from viktor.result import SetParamsResult
from viktor.views import ImageView

def length(params:Munch, **kwargs):
    value=params.input.inputlength
    return value

def get_profile_types(params: Munch, **kwargs):
    file_path = (
        Path(__file__).parent
        / "profiles"
        / f"steel-profiles-{params.input.profile_type}.csv"
    )
    df = pd.read_csv(file_path, header=[2], skiprows=[3, 4, 5])
    return df["Profile"].values.tolist()
def get_profile_types_all(p, **kwargs):
    file_path = (
        Path(__file__).parent
        / "profiles"
        / f"steel-profiles-{p}.csv"
    )
    df = pd.read_csv(file_path, header=[2], skiprows=[3, 4, 5])
    return df["Profile"].values.tolist()

class Parametrization(ViktorParametrization):
    
    input = Tab("Input")
    input.hidden = HiddenField('hidden')
    input.profilehidden = HiddenField('profileinfo')
    input.length = NumberField("length of the profile", suffix="m", default = 1)
    input.nl74 = LineBreak()
    input.support1 = OptionField("support Type node 1", options=["Fixed", "Hinged", "Roll"], default = "Hinged")
    input.support2 = OptionField("support Type node 2", options=["Fixed", "Hinged", "Roll"], default = "Roll")

    input.nl44 = LineBreak()

    input.LL = NumberField("LiveLoad", suffix="kN/m", default = "-3")
    input.DL = NumberField("DeadLoad", suffix="kN/m", default = "-2")

    input.nl1 = LineBreak()
    input.include_weight = OptionField("Include selfweight", options=["Yes", "No"], default="Yes", variant="radio-inline")
    input.nl2 = LineBreak()
    input.building_category = OptionField("building category", options = ["A, domestic/residential", "B, offices", "C, congregatoin areas", "D, Shopping areas", "E, Storage areas", "F, light traffic area", "G, heavy traffic area", "H, roofs"], default="A, domestic/residential")
    input.consequence_class = OptionField("Concequence class", options=["CCI", "CCII", "CCIII"], default="CCII")
    input.nl3 = LineBreak()
    input.profile_type = OptionField(
        "Profile type",
        options=["IPE", "HEA", "HEB", "HEM"],
        default="HEA",
        variant="radio-inline",
        flex=80,
    )
    input.nl4 = LineBreak()
    input.profile = AutocompleteField(
        "Profile",
        options=get_profile_types,
        default="HEA240",
        description="The source of profile properties can be found [here](https://eurocodeapplied.com/design/en1993/ipe-hea-heb-hem-design-properties)",
    )
    input.steel_class = OptionField(
        "Steel class", options=["S235", "S355"], default="S235"
    )
    input.nl445 = LineBreak()
    input.chosenprofile = TextField("chosen profile")

    optimize = Tab("optimization")
    optimize.maximum_deflection_all = OptionField('Δmax all loads', options=['1/250', '1/300', '1/500'], default='1/300')
    optimize.nl1 = LineBreak()
    optimize.maximum_deflection_LL = OptionField('Δmax live loads', options=['1/300', '1/500', '1/1000'], default='1/500')
    optimize.nl2 = LineBreak()
    optimize.maximum_utility = NumberField("U", default=0.8)
    optimize.nl3 = LineBreak()
    optimize.co2 = NumberField("co2 steel", suffix="co2/kg", default=2.89)
    optimize.nl4 = LineBreak()
    optimize.price_235 = NumberField("S235", suffix="€/kg", default=3.145)
    optimize.price_355 = NumberField("S355", suffix="€/kg", default=3.669)
    optimize.nl5 = LineBreak()
    optimize.optimize = OptimizationButton(
        "Find optimal profile",
        "optimize_profile",
        longpoll=True,
        flex=35,
        description="The optimization is based on the von mises stress and maximum deflections",
    )
    
class BeamController(ViktorController):
    viktor_enforce_field_constraints = (
        True  # Resolves upgrade instruction https://docs.viktor.ai/sdk/upgrades#U83
    )

    label = "Steel Beams"
    parametrization = Parametrization(width=30)

    def optimize_profile(self, params: Munch, storage=None, **kwargs):
        """Initiates the process of optimizing structure based on the bending moment unity check.
        The optimization considers the different profiles available.
        """
        print('yes')
        steel_classes = ["S235", "S355"]
        profile_types = ["IPE", "HEA", "HEB", "HEM"]
        co2 = params.optimize.co2
        results = []
        for s in steel_classes:

            for p in profile_types:
                profiles = get_profile_types_all(p)

                for profile in profiles:
                    params["input"]["profile"] = profile
                    params["input"]["profile_type"]= p
                    params["input"]["steel_class"] = s
                    length_list = []
                    weight = []
                    profilelist=[]
                    profile_weight = self.get_profile_property(p, profile, "Weight")
                    result_dict = self.create_model(params)
                    combination_ULS = result_dict['ULS']['combination']
                    max_moment = max([abs(val) for val in combination_ULS.get_element_result_range('moment')])
                    _, moment = combination_ULS.plot_values.bending_moment(1)
                    _, shear = combination_ULS.plot_values.shear_force(1)
                    _, axial = combination_ULS.plot_values.axial_force(1)
                    yield_strength = self.calculate_allowable_bending_moment(p, profile, s)["yield_strength"]
                    h = self.calculate_allowable_bending_moment(p, profile, s)["profile_height"]
                    b = self.calculate_allowable_bending_moment(p, profile, s)["profile_width"]
                    tf = self.calculate_allowable_bending_moment(p, profile, s)["profile_tf"]
                    tw = self.calculate_allowable_bending_moment(p, profile, s)["profile_tw"]
                    r = self.calculate_allowable_bending_moment(p, profile, s)["profile_r"]
                    a = self.calculate_allowable_bending_moment(p, profile, s)["profile_area"]
                    i = self.calculate_allowable_bending_moment(p, profile, s)["moment_of_inertia"]
                    wel = self.calculate_allowable_bending_moment(p, profile, s)["profile_wel"]
                    profilelist.append([profile,h,b,tw,tf,r])
                    moment_factor = max_moment / max(abs(moment))
                    correct_moment = moment * moment_factor
                    m = ((correct_moment * 1000000 * (h / 2 - tf)) / (wel * 1000 * h / 2))
                    v = (axial * 1000 / a)
                    t = (shear * 1000 * tf * b * (h - tf) / 2) / (tw * i * (10 ** 6))
                    vonmises_list = ((m + v) ** 2 + 3 * (t) ** 2) ** 0.5
                    vonmises = max(abs(vonmises_list))
                    unity = vonmises/yield_strength
                    allowable_moment = self.calculate_allowable_bending_moment(p, profile, s)["allowable_bending_moment"]
                    uc = abs(max_moment / allowable_moment)
                    pricea = params.optimize.price_235
                    priceb = params.optimize.price_355
                    if unity < params.optimize.maximum_utility:
                        combination_SLS = result_dict['SLS']['combination']
                        wmin_dict={}
                        wmax_dict = {}
                        node_defl = {}
                        lengths = {}
                        value = []

                        for dict in combination_SLS.get_element_results(verbose=True):
                            node_deflection_1 = combination_SLS.get_node_displacements(dict['id'])['uy']
                            node_deflection_2 = combination_SLS.get_node_displacements(int(dict['id']) + 1)['uy']
                            node_defl[dict['id']] = max(abs(node_deflection_1), abs(node_deflection_2))
                            wmin_dict[dict['id']] = dict['wmin']
                            wmax_dict[dict['id']] = dict['wmax']
                            lengths[dict['id']] = dict['length']

                        comparison_result = {}
                        for key in wmin_dict.keys():
                            max_abs_val = max(abs(wmin_dict[key]), abs(wmax_dict[key]), abs(node_defl[key]))
                            comparison_result[key] = max_abs_val
                        for e in wmin_dict.keys():
                            value.append(lengths[e] / comparison_result[e])

                        Deflection = int(min(value))
                        string_defl = params.optimize.maximum_deflection_all
                        parts = string_defl.split('/')
                        max_deflection = float(parts[1])

                        if Deflection >= max_deflection:
                            deflection_LL = result_dict['SLS']['LL']
                            wmin_LL = {}
                            wmax_LL = {}
                            node_defl_LL = {}
                            value_LL = []
                            for dict_LL in deflection_LL.get_element_results(verbose=True):
                                node_deflection_1_LL = deflection_LL.get_node_displacements(dict_LL['id'])['uy']
                                node_deflection_2_LL = deflection_LL.get_node_displacements(int(dict_LL['id']) + 1)['uy']
                                node_defl_LL[dict_LL['id']] = max(abs(node_deflection_1_LL), abs(node_deflection_2_LL))
                                wmin_LL[dict_LL['id']] = dict_LL['wmin']
                                wmax_LL[dict_LL['id']] = dict_LL['wmax']
                                lengths[dict_LL['id']] = dict_LL['length']

                            comparison_result_LL = {}
                            for key in wmin_LL.keys():
                                max_abs_val = max(abs(wmin_LL[key]), abs(wmax_LL[key]), abs(node_defl_LL[key]))
                                comparison_result_LL[key] = max_abs_val
                            for e in comparison_result_LL.keys():
                                value_LL.append(lengths[e] / wmin_LL[e])
                                weight.append(lengths[e]*profile_weight)
                                length_list.append(lengths[e])
                            Deflection_LL = int(min(value_LL))
                            string_defl_LL = params.optimize.maximum_deflection_LL
                            parts_LL = string_defl_LL.split('/')
                            max_deflection_LL = float(parts_LL[1])

                            if Deflection_LL >= max_deflection_LL:
                                total_weight=sum(weight)
                                total_length=sum(length_list)

                                if s == "S235":
                                    price=total_weight*pricea
                                else:
                                    price=total_weight*priceb
                                
                                print(profilelist)

                                results.append({"input": {"chosenprofile":str(profilelist), "profilehidden": profilelist, "profile": profile, "steel_class": s, "profile_type":p }, "unity_check": round(unity, 2), "U_bending":round(uc,2), 'max_deflection': Deflection, 'max_deflection_LL': Deflection_LL, 'total_weight':round(total_weight,2), 'CO²_equivalent':round(total_weight*co2,2), 'CO²m':round(total_weight*co2/total_length,2), 'price':round(price,1), 'pricem':round(price/total_length,1)})
                                break

        output_headers = {"unity_check": "Unity check",
                          'max_deflection': 'maximum deflection: L/',
                          'max_deflection_LL': 'maximum additional deflection: L/', 'total_weight': 'total weight (kg)',
                          'CO²_equivalent': 'CO² equivalent', 'CO²m': 'CO² equivalent /m', 'price': 'price (€)',
                          'pricem': 'price/m (€/m)'}

        input_column = ['input.profile', 'input.steel_class']
        # storage = Storage()
        # storage.set('results_steel', data=File.from_data(json.dumps(results)), scope='entity')
        results_as_optimizationresultelements = [OptimizationResultElement({'input': result.pop('input')}, result) for result in results]

        




        return OptimizationResult(results_as_optimizationresultelements, input_column,  output_headers=output_headers)

    def create_model(self, params: Munch, solve_model=True):
        """Creates and returns an anastruct `SystemElements` model based on the app's given parameters.

        :param params: Munch object of the app's parametrization.
        :param solve_model: Boolean input to indicate whether to solve the initialized model.
        :return: `anastruct.SystemElements` object.
        """

        youngs_modulus = 210000 * 10**3  # kN/m2
        profile_type = params.input.profile_type
        profile = params.input.profile
        moment_of_inertia = (self.get_profile_property(profile_type, profile, "Second moment of area")/ 10**6)  # Convert x10^6 mm4 to m4
        ss = SystemElements(EI=youngs_modulus * moment_of_inertia)

        if params.input.include_weight=='Yes':
            weight = (
                self.get_profile_property(profile_type, profile, "Weight") * 9.81 / 1000
            )  # Convert kg/m to kN/m
        else:
            weight = 0

        # Create elements
        length = params.input.length
        ss.add_element(location=[[0, 0], [length, 0]], g=weight)

        # Create supports
        if params.input.support1 == "Fixed":
            ss.add_support_fixed(node_id=1)
        elif params.input.support1 == "Hinged":
            ss.add_support_hinged(node_id=1)
        elif params.input.support1 == "Roll":
            ss.add_support_roll(node_id=1, direction=2)

        if params.input.support2 == "Fixed":
            ss.add_support_fixed(node_id=2)
        elif params.input.support2 == "Hinged":
            ss.add_support_hinged(node_id=2)
        elif params.input.support2 == "Roll":
            ss.add_support_roll(node_id=2, direction=2)

        lc_dl = LoadCase('DL')
        lc_ll = LoadCase('LL')

        # Create distributed loads
        lc_dl.q_load(q= params.input.DL or 0.0000000000000000001 - weight, element_id=1, direction="element")
        lc_ll.q_load(q=params.input.LL or 0.0000000000000000001, element_id=1, direction="element")

        CC_dict = {"CCI": 0.9, "CCII": 1, "CCIII": 1.1}
        CC = CC_dict.get(params.input.consequence_class)

        combination_ULS = LoadCombination('ULS')
        combination_ULS.add_load_case(lc_dl, 1.35*CC)
        combination_ULS.add_load_case(lc_ll,1.5*CC)

        combination_SLS = LoadCombination('SLS')
        combination_SLS.add_load_case(lc_dl, 1)
        combination_SLS.add_load_case(lc_ll, 1)


        # Solve the model
        if solve_model:
            try:
                ss.remove_loads()
                result_ULS = combination_ULS.solve(ss)
                ss.remove_loads()
                result_SLS = combination_SLS.solve(ss)

            except:
                raise UserError(
                    "Calculation cannot be solved, check if you have a LL and a DL, check supports"
                )

        return {'SLS': result_SLS, 'ULS': result_ULS}

    @staticmethod
    def get_profile_property(profile_type: str, profile: str, property_name: str) -> float:
        """Retrieve the profile properties based on the profile type, profile and property

        :param profile_type: One of the following profile types: HEA, HEB or IPE.
        :param profile: Profile name, e.g. IPE80 (IPE was given as profile_type)
        :param property_name: The name of the property, e.g. Weight
        """
        file_path = (
            Path(__file__).parent / "profiles" / f"steel-profiles-{profile_type}.csv"
        )
        df = pd.read_csv(file_path, header=[2], skiprows=[3, 4, 5])
        return df.loc[df["Profile"] == profile, property_name].item()
    @staticmethod
    def calculate_allowable_bending_moment(profile_type: str, profile: str, steel_class: str):
        """Calculates the allowable bending moment based on the given parameters.

        :param profile_type: One of the following profile types: HEA, HEB or IPE.
        :param profile: Profile name, e.g. IPE80 (IPE was given as profile_type)
        :param steel_class: The steel class, e.g. S235
        :return: A dict with the moment of inertia, profile height, yield strength and allowable bending moment.
        """
        file_path = (
            Path(__file__).parent / "profiles" / f"steel-profiles-{profile_type}.csv"
        )
        df = pd.read_csv(file_path, header=[2], skiprows=[3, 4, 5])
        moment_of_inertia = df.loc[df["Profile"] == profile, "Second moment of area"].item()
        profile_width = df.loc[df["Profile"] == profile, "Width"].item()
        profile_height = df.loc[df["Profile"] == profile, "Depth"].item()
        profile_tw = df.loc[df["Profile"] == profile, "Web thickness"].item()
        profile_tf = df.loc[df["Profile"] == profile, "Flange thickness"].item()
        profile_r = df.loc[df["Profile"] == profile, "Root radius"].item()
        profile_wel = df.loc[df["Profile"] == profile, "Elastic section modulus"].item()
        profile_area = df.loc[df["Profile"] == profile, "Area"].item()
        profile_wpl = df.loc[df["Profile"] == profile, "Plastic section modulus"].item()

        yield_strength = float(
            steel_class[-3:]
        )  # Yield strength is based on the steel class, i.e. the yields strength of S235 is 235MPa
        allowable_bending_moment = (yield_strength * moment_of_inertia) / (
            profile_height / 2
        )
        return {
            "moment_of_inertia": moment_of_inertia,
            "profile_height": profile_height,
            "profile_width":profile_width,
            "profile_tw":profile_tw,
            "profile_tf":profile_tf,
            "profile_wel":profile_wel,
            "profile_wpl":profile_wpl,
            "profile_r":profile_r,
            "profile_area":profile_area,
            "yield_strength": yield_strength,
            "allowable_bending_moment": allowable_bending_moment,
        }

    @ImageView("Structure DL", duration_guess=1)
    def create_structure_DL(self, params: Munch, **kwargs):
        """Initiates the process of rendering the structure visualization."""
        result_dict = self.create_model(params)
        DL = result_dict['SLS']['DL']
        fig = DL.show_structure(show=False)
        return ImageResult(self.fig_to_svg(fig))

    @ImageView("Structure LL", duration_guess=1)
    def create_structure_LL(self, params: Munch, **kwargs):
        """Initiates the process of rendering the structure visualization."""
        result_dict = self.create_model(params)
        LL = result_dict['SLS']['LL']
        fig = LL.show_structure(show=False)
        return ImageResult(self.fig_to_svg(fig))
    @staticmethod
    def fig_to_svg(fig: Figure) -> StringIO:
        svg_data = StringIO()
        fig.savefig(svg_data, format="svg")
        return svg_data
        
    def summary_update(self, params, **kwargs):
        p= params.hidden
        if p == None:
            q=1
        else:
            q=p+1
        print (q)
        return SetParamsResult({'input.hidden':q})


    summary = Summary(item_1=SummaryItem('length', float, 'parametrization','input.length'))
                      
    