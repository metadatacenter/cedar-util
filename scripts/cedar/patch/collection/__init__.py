from cedar.patch.collection.AddContentToUiPatch import AddContentToUiPatch
from cedar.patch.collection.AddIdToPropertiesPatch import AddIdToPropertiesPatch
from cedar.patch.collection.AddMissingContextPatch import AddMissingContextPatch
from cedar.patch.collection.AddMultipleChoiceToValueConstraintsPatch import AddMultipleChoiceToValueConstraintsPatch
from cedar.patch.collection.AddOrderToUiPatch import AddOrderToUiPatch
from cedar.patch.collection.AddPropertyLabelsToUiPatch import AddPropertyLabelsToUiPatch
from cedar.patch.collection.AddProvenanceToContextPatch import AddProvenanceToContextPatch
from cedar.patch.collection.AddProvenanceToContextPropertiesPatch import AddProvenanceToContextPropertiesPatch
from cedar.patch.collection.AddProvenanceToFieldOrElementPatch import AddProvenanceToFieldOrElementPatch
from cedar.patch.collection.AddProvenanceToPropertiesPatch import AddProvenanceToPropertiesPatch
from cedar.patch.collection.AddRdfsLabelToContextPropertiesPatch import AddRdfsLabelToContextPropertiesPatch
from cedar.patch.collection.AddRdfsLabelToPropertiesPatch import AddRdfsLabelToPropertiesPatch
from cedar.patch.collection.AddRdfsToContextPropertiesPatch import AddRdfsToContextPropertiesPatch
from cedar.patch.collection.AddRequiredToFieldOrElementPatch import AddRequiredToFieldOrElementPatch
from cedar.patch.collection.AddSchemaDescriptionToContextPatch import AddSchemaDescriptionToContextPatch
from cedar.patch.collection.AddSchemaDescriptionToContextPropertiesPatch import AddSchemaDescriptionToContextPropertiesPatch
from cedar.patch.collection.AddSchemaIsBasedOnToContextPropertiesPatch import AddSchemaIsBasedOnToContextPropertiesPatch
from cedar.patch.collection.AddSchemaNameToContextPatch import AddSchemaNameToContextPatch
from cedar.patch.collection.AddSchemaNameToContextPropertiesPatch import AddSchemaNameToContextPropertiesPatch
from cedar.patch.collection.AddSchemaPropsToPropertiesPatch import AddSchemaPropsToPropertiesPatch
from cedar.patch.collection.AddSchemaToContextPatch import AddSchemaToContextPatch
from cedar.patch.collection.AddSchemaVersionPatch import AddSchemaVersionPatch
from cedar.patch.collection.AddValueConstraintsToFieldOrElementPatch import AddValueConstraintsToFieldOrElementPatch
from cedar.patch.collection.AddXsdToContextPatch import AddXsdToContextPatch
from cedar.patch.collection.AddXsdToContextPropertiesPatch import AddXsdToContextPropertiesPatch
from cedar.patch.collection.FillEmptyValuePatch import FillEmptyValuePatch
from cedar.patch.collection.FillNullValuePatch import FillNullValuePatch
from cedar.patch.collection.MoveTitleAndDescriptionPatch import MoveTitleAndDescriptionPatch
from cedar.patch.collection.MoveTitlePatch import MoveTitlePatch
from cedar.patch.collection.MoveDescriptionPatch import MoveDescriptionPatch
from cedar.patch.collection.MoveContentToUiPatch import MoveContentToUiPatch
from cedar.patch.collection.NoMatchOutOfFiveSchemasPatch import NoMatchOutOfFiveSchemasPatch
from cedar.patch.collection.NoMatchOutOfTwoSchemasPatch import NoMatchOutOfTwoSchemasPatch
from cedar.patch.collection.RecreateElementRequiredPatch import RecreateElementRequiredPatch
from cedar.patch.collection.RecreateTemplateRequiredPatch import RecreateTemplateRequiredPatch
from cedar.patch.collection.RemoveArrayDuplicatesPatch import RemoveArrayDuplicatesPatch
from cedar.patch.collection.RemoveEnumFromOneOfPatch import RemoveEnumFromOneOfPatch
from cedar.patch.collection.RemoveEnumFromTypePatch import RemoveEnumFromTypePatch
from cedar.patch.collection.RemoveIdFromPropertiesPatch import RemoveIdFromPropertiesPatch
from cedar.patch.collection.RemoveInstanceOfPatch import RemoveInstanceOfPatch
from cedar.patch.collection.RemoveOslcFromElementContextPropertiesPatch import RemoveOslcFromElementContextPropertiesPatch
from cedar.patch.collection.RemoveValueFromPropertiesPatch import RemoveValueFromPropertiesPatch
from cedar.patch.collection.RemovePageFromInnerUiPatch import RemovePageFromInnerUiPatch
from cedar.patch.collection.RemovePatternPropertiesPatch import RemovePatternPropertiesPatch
from cedar.patch.collection.RemovePavFromElementContextPropertiesPatch import RemovePavFromElementContextPropertiesPatch
from cedar.patch.collection.RemoveSchemaFromElementContextPropertiesPatch import RemoveSchemaFromElementContextPropertiesPatch
from cedar.patch.collection.RemoveXsdFromElementContextPropertiesPatch import RemoveXsdFromElementContextPropertiesPatch
from cedar.patch.collection.RemoveProvenanceFromPropertiesPatch import RemoveProvenanceFromPropertiesPatch
from cedar.patch.collection.RemoveSchemaDescriptionFromPropertiesPatch import RemoveSchemaDescriptionFromPropertiesPatch
from cedar.patch.collection.RemoveSchemaIsBasedOnFromPropertiesPatch import RemoveSchemaIsBasedOnFromPropertiesPatch
from cedar.patch.collection.RemoveSchemaNameFromPropertiesPatch import RemoveSchemaNameFromPropertiesPatch
from cedar.patch.collection.RemoveSchemaVersionPatch import RemoveSchemaVersionPatch
from cedar.patch.collection.RemoveSelectionTypeFromUiPatch import RemoveSelectionTypeFromUiPatch
from cedar.patch.collection.RemoveTemplateIdFromPropertiesPatch import RemoveTemplateIdFromPropertiesPatch
from cedar.patch.collection.RemoveUiFromPropertiesPatch import RemoveUiFromPropertiesPatch
from cedar.patch.collection.RenameValueLabelToRdfsLabelPatch import RenameValueLabelToRdfsLabelPatch
from cedar.patch.collection.RestructureStaticTemplateFieldPatch import RestructureStaticTemplateFieldPatch
from cedar.patch.collection.RestructureMultiValuedFieldPatch import RestructureMultiValuedFieldPatch
from cedar.patch.collection.AddBiboToContextPatch import AddBiboToContextPatch
from cedar.patch.collection.AddVersioningPatch import AddVersioningPatch
from cedar.patch.collection.AddVersioningInNestedElementPatch import AddVersioningInNestedElementPatch
from cedar.patch.collection.AddVersioningInNestedMultiElementPatch import AddVersioningInNestedMultiElementPatch
from cedar.patch.collection.AddBiboStatusPatch import AddBiboStatusPatch
from cedar.patch.collection.AddBiboVersionPatch import AddBiboVersionPatch
from cedar.patch.collection.FillEmptyPropertyDescriptionPatch import FillEmptyPropertyDescriptionPatch
from cedar.patch.collection.RecreateAdditionalValuePatch import RecreateAdditionalValuePatch
from cedar.patch.collection.AddSkosToContextPatch import AddSkosToContextPatch
from cedar.patch.collection.AddSkosToContextPropertiesPatch import AddSkosToContextPropertiesPatch
from cedar.patch.collection.AddSkosNotationToContextPropertiesPatch import AddSkosNotationToContextPropertiesPatch
from cedar.patch.collection.AddSkosPrefLabelToContextPatch import AddSkosPrefLabelToContextPatch
from cedar.patch.collection.AddSkosAltLabelToContextPatch import AddSkosAltLabelToContextPatch


__all__ = [
    "AddContentToUiPatch",
    "AddIdToPropertiesPatch",
    "AddMissingContextPatch",
    "AddMultipleChoiceToValueConstraintsPatch",
    "AddOrderToUiPatch",
    "AddPropertyLabelsToUiPatch",
    "AddProvenanceToContextPatch",
    "AddProvenanceToContextPropertiesPatch",
    "AddProvenanceToFieldOrElementPatch",
    "AddProvenanceToPropertiesPatch",
    "AddRequiredToFieldOrElementPatch",
    "AddSchemaDescriptionToContextPatch",
    "AddSchemaDescriptionToContextPropertiesPatch",
    "AddSchemaIsBasedOnToContextPropertiesPatch",
    "AddSchemaNameToContextPatch",
    "AddSchemaNameToContextPropertiesPatch",
    "AddSchemaPropsToPropertiesPatch",
    "AddSchemaToContextPatch",
    "AddRdfsLabelToContextPropertiesPatch",
    "AddRdfsLabelToPropertiesPatch",
    "AddRdfsToContextPropertiesPatch",
    "AddSchemaVersionPatch",
    "AddValueConstraintsToFieldOrElementPatch",
    "AddXsdToContextPatch",
    "AddXsdToContextPropertiesPatch",
    "AddSkosToContextPatch",
    "AddSkosToContextPropertiesPatch",
    "AddSkosNotationToContextPropertiesPatch",
    "AddSkosPrefLabelToContextPatch",
    "AddSkosAltLabelToContextPatch",
    "FillEmptyValuePatch",
    "FillNullValuePatch",
    "MoveTitleAndDescriptionPatch",
    "MoveTitlePatch",
    "MoveDescriptionPatch",
    "MoveContentToUiPatch",
    "NoMatchOutOfFiveSchemasPatch",
    "NoMatchOutOfTwoSchemasPatch",
    "RecreateElementRequiredPatch",
    "RecreateTemplateRequiredPatch",
    "RemoveArrayDuplicatesPatch",
    "RemoveEnumFromOneOfPatch",
    "RemoveEnumFromTypePatch",
    "RemoveIdFromPropertiesPatch",
    "RemoveInstanceOfPatch",
    "RemoveOslcFromElementContextPropertiesPatch",
    "RemoveValueFromPropertiesPatch",
    "RemovePageFromInnerUiPatch",
    "RemovePatternPropertiesPatch",
    "RemovePavFromElementContextPropertiesPatch",
    "RemoveSchemaFromElementContextPropertiesPatch",
    "RemoveXsdFromElementContextPropertiesPatch",
    "RemoveProvenanceFromPropertiesPatch",
    "RemoveSchemaDescriptionFromPropertiesPatch",
    "RemoveSchemaIsBasedOnFromPropertiesPatch",
    "RemoveSchemaNameFromPropertiesPatch",
    "RemoveSchemaVersionPatch",
    "RemoveSelectionTypeFromUiPatch",
    "RemoveTemplateIdFromPropertiesPatch",
    "RemoveUiFromPropertiesPatch",
    "RenameValueLabelToRdfsLabelPatch",
    "RestructureMultiValuedFieldPatch",
    "RestructureStaticTemplateFieldPatch",
    "AddBiboToContextPatch",
    "AddVersioningPatch",
    "AddVersioningInNestedElementPatch",
    "AddVersioningInNestedMultiElementPatch",
    "AddBiboStatusPatch",
    "AddBiboVersionPatch",
    "FillEmptyPropertyDescriptionPatch",
    "RecreateAdditionalValuePatch"]