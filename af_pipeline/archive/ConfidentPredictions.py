from af_pipeline._Initialize import _Initialize
from af_pipeline.Parser import ResidueSelect
# from af_pipeline.archive.af_utils import save_pdb, renumber_res_dict, renumber_residues


class ConfidentPredictions(_Initialize):
    """ Save confident residues as a PDB file.

    a confident residue is defined as a residue if- \n
    1. it has Ca-pLDDT score >= plddt_cutoff and \n
    2. it has avg PAE <= pae_cutoff with at least one other residue in any of the partner chains. \n
    """

    def __init__(
        self,
        struct_file_path: str,
        data_file_path: str,
        out_file: str,
        af_offset: dict | None = None,
    ):
        super().__init__(
            data_file_path=data_file_path,
            struct_file_path=struct_file_path,
            af_offset=af_offset,
        )

        self.out_file = out_file
        self.apply_plddt = True
        self.apply_pae = True
        self.plddt_cutoff = 70
        self.pae_cutoff = 5

    def save_confident_regions(self):
        """
        Select confident residues based on plddt and min_pae. \n
        Save the confident residues as a PDB file.
        """

        confident_residues = {}

        if not self.apply_plddt and not self.apply_pae:
            raise Exception("No confidence filter applied...")

        for chain in self.res_dict:
            confident_residues[chain] = []
            for res in self.res_dict[chain]:

                # Get index from residue position.
                idx = res - 1
                select = False
                if self.apply_plddt:
                    if self.plddt_dict[chain][idx] >= self.plddt_cutoff:
                        select = True

                if self.apply_pae:
                    # print( self.min_pae_dict[chain][idx] )
                    if self.min_pae_dict[chain][idx] <= self.pae_cutoff:
                        select = True

                if select:
                    confident_residues[chain].append(res)

        structure = renumber_residues(
            structure=self.structureparser.structure,
            af_offset=self.af_offset,
        )
        confident_residues = renumber_res_dict(
            res_dict=confident_residues,
            af_offset=self.af_offset,
        )

        save_pdb(
            structure=structure,
            out_file=self.out_file,
            res_select_obj=ResidueSelect(confident_residues),
        )